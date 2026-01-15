import re
from paddleocr import PaddleOCR

class NutritionOCRService:
    def __init__(self, use_gpu=False):
        kwargs = {
            "use_angle_cls": True,
            "lang": "korean",

            # 아래는 버전에 따라 지원 안 할 수 있음 → 에러나면 자동 제거됨
            "use_gpu": use_gpu,
            "show_log": False,
            "drop_score": 0.2,
            "det_db_box_thresh": 0.3,
            "det_db_unclip_ratio": 2.0,
        }

        while True:
            try:
                self.ocr = PaddleOCR(**kwargs)
                break
            except Exception as e:
                msg = str(e)
                m = re.search(r"Unknown argument:\s*([A-Za-z0-9_]+)", msg)
                if m:
                    bad = m.group(1)
                    kwargs.pop(bad, None)
                    continue
                raise
