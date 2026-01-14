# import cv2
# import numpy as np
# import re
# import os
# from paddleocr import PaddleOCR

# class NutritionOCRService:
#     def __init__(self, use_gpu=False):
#         # drop_score를 낮춰서(=덜 버리게) 핵심 라인 누락 방지
#         self.ocr = PaddleOCR(
#             use_angle_cls=True,
#             lang="korean",
#             show_log=False,
#             use_gpu=use_gpu,
#             drop_score=0.2,                 # 중요: 0.5 -> 0.2
#             det_db_box_thresh=0.3,          # 텍스트 박스 더 잘 잡게
#             det_db_unclip_ratio=2.0
#         )

#         self.keywords = ["kcal", "탄수화물", "단백질", "지방", "열량", "칼로리"]

#     # ---------- 이미지 전처리(핵심) ----------
#     def _order_points(self, pts):
#         pts = np.array(pts, dtype=np.float32)
#         rect = np.zeros((4, 2), dtype=np.float32)
#         s = pts.sum(axis=1)
#         diff = np.diff(pts, axis=1)

#         rect[0] = pts[np.argmin(s)]      # top-left
#         rect[2] = pts[np.argmax(s)]      # bottom-right
#         rect[1] = pts[np.argmin(diff)]   # top-right
#         rect[3] = pts[np.argmax(diff)]   # bottom-left
#         return rect

#     def _warp_largest_rectangle(self, img):
#         """
#         영양성분표는 보통 큰 사각 테두리/박스라서,
#         가장 큰 4각형 컨투어를 찾아 원근 보정한다.
#         """
#         gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
#         blur = cv2.GaussianBlur(gray, (5, 5), 0)
#         edges = cv2.Canny(blur, 50, 150)

#         contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
#         contours = sorted(contours, key=cv2.contourArea, reverse=True)

#         for c in contours[:10]:
#             peri = cv2.arcLength(c, True)
#             approx = cv2.approxPolyDP(c, 0.02 * peri, True)
#             if len(approx) == 4 and cv2.contourArea(approx) > 0.15 * (img.shape[0] * img.shape[1]):
#                 rect = self._order_points(approx.reshape(4, 2))
#                 (tl, tr, br, bl) = rect

#                 widthA = np.linalg.norm(br - bl)
#                 widthB = np.linalg.norm(tr - tl)
#                 maxW = int(max(widthA, widthB))

#                 heightA = np.linalg.norm(tr - br)
#                 heightB = np.linalg.norm(tl - bl)
#                 maxH = int(max(heightA, heightB))

#                 dst = np.array([
#                     [0, 0],
#                     [maxW - 1, 0],
#                     [maxW - 1, maxH - 1],
#                     [0, maxH - 1]
#                 ], dtype=np.float32)

#                 M = cv2.getPerspectiveTransform(rect, dst)
#                 warped = cv2.warpPerspective(img, M, (maxW, maxH))
#                 return warped

#         # 못 찾으면 원본 그대로
#         return img

#     def _pad(self, img, pad=20, value=255):
#         if len(img.shape) == 2:
#             return cv2.copyMakeBorder(img, pad, pad, pad, pad, cv2.BORDER_CONSTANT, value=value)
#         return cv2.copyMakeBorder(img, pad, pad, pad, pad, cv2.BORDER_CONSTANT, value=(value, value, value))

#     def preprocess_variants(self, image_path):
#         img = cv2.imread(image_path)
#         if img is None:
#             raise ValueError(f"이미지를 읽을 수 없습니다: {image_path}")

#         # 1) 큰 사각형(라벨) 원근보정
#         warped = self._warp_largest_rectangle(img)

#         # 2) 크기 확대(작은 글자 대비)
#         h, w = warped.shape[:2]
#         scale = 2.5 if w < 1400 else 1.8
#         resized = cv2.resize(warped, (int(w * scale), int(h * scale)), interpolation=cv2.INTER_CUBIC)

#         # 3) 여러 버전 만들기(한 장만 쓰면 실패 케이스가 생김)
#         gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
#         gray = self._pad(gray, pad=25, value=255)

#         # 대비 향상
#         clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
#         enhanced = clahe.apply(gray)

#         # 이진화 2종
#         blur = cv2.GaussianBlur(enhanced, (3, 3), 0)
#         _, otsu = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
#         adaptive = cv2.adaptiveThreshold(
#             blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
#             cv2.THRESH_BINARY, 31, 5
#         )

#         # 반전본도 같이(검정바탕 흰글씨 부분이 잘릴 때 대비)
#         inv_otsu = cv2.bitwise_not(otsu)
#         inv_adapt = cv2.bitwise_not(adaptive)

#         # 원본(리사이즈)도 같이(이진화가 오히려 망치는 케이스 대비)
#         rgb = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)

#         return [
#             ("rgb", rgb),                 # PaddleOCR은 ndarray 입력 가능
#             ("enhanced", enhanced),
#             ("otsu", otsu),
#             ("adaptive", adaptive),
#             ("inv_otsu", inv_otsu),
#             ("inv_adaptive", inv_adapt),
#         ]

#     # ---------- OCR ----------
#     def extract_text_lines(self, img_variant):
#         """
#         PaddleOCR 결과를 줄 단위로 정렬해서 반환.
#         """
#         result = self.ocr.ocr(img_variant, cls=True)
#         lines = []
#         if not result or not result[0]:
#             return []

#         for item in result[0]:
#             box = item[0]
#             text, score = item[1]
#             if not text:
#                 continue
#             # y, x 기준 정렬용
#             ys = [p[1] for p in box]
#             xs = [p[0] for p in box]
#             lines.append((min(ys), min(xs), text, score))

#         # 위->아래, 왼->오 정렬
#         lines.sort(key=lambda x: (x[0], x[1]))
#         return [t for _, _, t, _ in lines]

#     def pick_best_ocr(self, variants):
#         """
#         여러 전처리 버전 중 가장 '영양성분표'답게 나온 텍스트를 선택
#         """
#         best_lines = []
#         best_score = -1

#         for name, img in variants:
#             lines = self.extract_text_lines(img)
#             joined = " ".join(lines).replace(" ", "")

#             # 키워드 히트 수로 점수
#             hit = sum(1 for k in self.keywords if k in joined)
#             # 숫자(=영양값) 존재도 가산
#             nums = len(re.findall(r"\d+(?:\.\d+)?", joined))
#             score = hit * 10 + min(nums, 30)

#             if score > best_score:
#                 best_score = score
#                 best_lines = lines

#         return best_lines

#     # ---------- 파싱 ----------
#     def _normalize(self, s: str) -> str:
#         s = s.replace(",", "")
#         s = s.replace("O", "0").replace("o", "0")  # 가끔 0/O 혼동
#         return s

#     def _extract_amount(self, line: str, key: str):
#         """
#         key(탄수화물/단백질/지방) 라인에서 수치와 단위 추출.
#         mg/g 없으면 숫자만이라도 잡고 g로 간주.
#         """
#         s = self._normalize(line)

#         # 1) 단위 포함 (g/mg)
#         m = re.search(rf"{key}[^0-9]*?(\d+(?:\.\d+)?)\s*(mg|g)", s)
#         if m:
#             val = float(m.group(1))
#             unit = m.group(2)
#             return val, unit

#         # 2) 단위 누락 fallback: key 다음 첫 숫자
#         m = re.search(rf"{key}[^0-9]*?(\d+(?:\.\d+)?)", s)
#         if m:
#             val = float(m.group(1))
#             return val, None

#         return None, None

#     def parse_nutrition_info_from_lines(self, lines):
#         """
#         탄/단/지는 g로 통일(mg면 /1000)
#         """
#         data = {
#             "calories_kcal": None,
#             "carbohydrates_g": None,
#             "protein_g": None,
#             "fat_g": None
#         }

#         # calories
#         joined = self._normalize(" ".join(lines))
#         m = re.search(r"(\d+(?:\.\d+)?)\s*k?cal", joined, re.IGNORECASE)
#         if not m:
#             m = re.search(r"(열량|칼로리)[^0-9]*?(\d+(?:\.\d+)?)", joined)
#             if m:
#                 data["calories_kcal"] = float(m.group(2))
#         else:
#             data["calories_kcal"] = float(m.group(1))

#         # 탄수화물/단백질: 해당 키가 있는 라인 우선
#         for key, out_key in [("탄수화물", "carbohydrates_g"), ("단백질", "protein_g")]:
#             candidates = [ln for ln in lines if key in ln]
#             for ln in candidates:
#                 val, unit = self._extract_amount(ln, key)
#                 if val is None:
#                     continue
#                 if unit == "mg":
#                     val /= 1000.0
#                 data[out_key] = val
#                 break

#         # 지방: "트랜스지방", "포화지방" 제외하고 "지방" 라인만 우선
#         fat_candidates = []
#         for ln in lines:
#             if "지방" in ln and ("트랜스지방" not in ln) and ("포화지방" not in ln):
#                 fat_candidates.append(ln)

#         for ln in fat_candidates:
#             val, unit = self._extract_amount(ln, "지방")
#             if val is None:
#                 continue
#             if unit == "mg":
#                 val /= 1000.0
#             data["fat_g"] = val
#             break

#         # 혹시 OCR이 라인 분리 실패해서 fat_candidates가 비면 joined에서 보정 추출
#         if data["fat_g"] is None:
#             # "지방"이 여러 번 나올 때 0g(트랜스/포화)보다 '처음 나오는 총지방'이 보통 더 앞에 있음
#             # 따라서 "지방숫자g" 패턴 중 트랜스/포화 붙은 건 제외하는 방식
#             s = joined
#             matches = re.findall(r"(?<!트랜스)(?<!포화)지방[^0-9]*?(\d+(?:\.\d+)?)\s*(mg|g)?", s)
#             if matches:
#                 val = float(matches[0][0])
#                 unit = matches[0][1] if matches[0][1] else None
#                 if unit == "mg":
#                     val /= 1000.0
#                 data["fat_g"] = val

#         return data

#     def analyze_nutrition_label(self, image_path):
#         variants = self.preprocess_variants(image_path)
#         best_lines = self.pick_best_ocr(variants)
#         nutrition = self.parse_nutrition_info_from_lines(best_lines)

#         # 보기 좋게 소수점 3자리(원하면 여기서 formatting만 바꾸면 됨)
#         def f3(x):
#             return None if x is None else float(f"{x:.3f}")

#         return {
#             "calories_kcal": f3(nutrition["calories_kcal"]),
#             "carbohydrates_g": f3(nutrition["carbohydrates_g"]),
#             "protein_g": f3(nutrition["protein_g"]),
#             "fat_g": f3(nutrition["fat_g"]),
#         }


# ocr_service.py (posts/services/ocr_service.py)
import cv2
import numpy as np
import re
import os
import json
import glob
import tempfile
from uuid import uuid4
from pathlib import Path
from paddleocr import PaddleOCR
from PIL import Image

class NutritionOCRService:
    _ocr = None

    def __init__(self):
        # PaddleOCR 3.x: predict() 기반
        if NutritionOCRService._ocr is None:
            NutritionOCRService._ocr = PaddleOCR(
                lang="korean",
                device="cpu",
                use_doc_orientation_classify=False,
                use_doc_unwarping=False,
                use_textline_orientation=False,
                # 필요하면 임계값 조절 가능 (3.x 파라미터)
                text_rec_score_thresh=0.0,
            )
        self.ocr = NutritionOCRService._ocr

    def _safe_imread(self, image_path: str):
        img = cv2.imread(image_path)
        if img is not None:
            return img
        # webp 등 cv2가 못 읽는 경우 PIL로 fallback
        pil = Image.open(image_path).convert("RGB")
        return cv2.cvtColor(np.array(pil), cv2.COLOR_RGB2BGR)

    def preprocess_image(self, image_path: str) -> str:
        img = self._safe_imread(image_path)

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        h, w = gray.shape
        if w < 1000:
            scale = 1000 / w
            gray = cv2.resize(gray, (int(w * scale), int(h * scale)), interpolation=cv2.INTER_CUBIC)

        denoised = cv2.fastNlMeansDenoising(gray, h=20)

        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(denoised)

        kernel = np.array([[-1,-1,-1],
                           [-1, 9,-1],
                           [-1,-1,-1]])
        sharpened = cv2.filter2D(enhanced, -1, kernel)

        _, binary = cv2.threshold(sharpened, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        k = np.ones((2,2), np.uint8)
        cleaned = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, k)

        out_path = os.path.join(tempfile.gettempdir(), f"ocr_processed_{uuid4().hex}.png")
        cv2.imwrite(out_path, cleaned)
        return out_path

    def _result_to_dict(self, res) -> dict:
        # 3.x는 res.print(), res.save_to_json() 제공 
        # 안전하게 json 파일로 저장 후 읽기
        with tempfile.TemporaryDirectory() as td:
            res.save_to_json(td)
            candidates = glob.glob(os.path.join(td, "**", "*.json"), recursive=True)
            if not candidates:
                return {}
            with open(candidates[0], "r", encoding="utf-8") as f:
                return json.load(f)

    def extract_texts(self, image_path: str, min_conf: float = 0.5):
        processed_path = self.preprocess_image(image_path)

        results = self.ocr.predict(processed_path)
        texts = []
        scores = []

        for res in results:
            data = self._result_to_dict(res)
            payload = data.get("res", {})
            rec_texts = payload.get("rec_texts", []) or []
            rec_scores = payload.get("rec_scores", []) or []

            # rec_scores가 list/array 형태 섞여올 수 있어서 float로 강제
            for t, s in zip(rec_texts, rec_scores):
                try:
                    sf = float(s)
                except:
                    continue
                if sf >= min_conf and t and str(t).strip():
                    texts.append(str(t).strip())
                    scores.append(sf)

        full_text = " ".join(texts)
        return full_text

    def parse_nutrition_info(self, text: str):
        data = {"calories": None, "carbohydrates": None, "protein": None, "fat": None}
        if not text:
            return data

        t = text.replace(" ", "").replace(",", "")

        # 칼로리
        m = re.search(r"(\d+(?:\.\d+)?)kcal", t, re.IGNORECASE)
        if m:
            data["calories"] = float(m.group(1))

        # 탄수화물
        m = re.search(r"탄수화물.*?(\d+(?:\.\d+)?)(mg|g)", t)
        if m:
            v = float(m.group(1))
            if m.group(2) == "mg":
                v /= 1000
            data["carbohydrates"] = v

        # 단백질
        m = re.search(r"단백질.*?(\d+(?:\.\d+)?)(mg|g)", t)
        if m:
            v = float(m.group(1))
            if m.group(2) == "mg":
                v /= 1000
            data["protein"] = v

        # 지방: 트랜스지방/포화지방 먼저 잡히는 문제 방지
        m = re.search(r"(?<!트랜스)(?<!포화)지방.*?(\d+(?:\.\d+)?)(mg|g)", t)
        if m:
            v = float(m.group(1))
            if m.group(2) == "mg":
                v /= 1000
            data["fat"] = v

        # 소수점 셋째자리 맞춤
        for k in data:
            if data[k] is not None:
                data[k] = round(float(data[k]), 3)

        return data

    def analyze_nutrition_label(self, image_path: str):
        extracted_text = self.extract_texts(image_path, min_conf=0.5)
        nutrition_info = self.parse_nutrition_info(extracted_text)
        return nutrition_info
