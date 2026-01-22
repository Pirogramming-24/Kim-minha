import os
import requests

#엔드포인트 버그 수정 > 요약 작동
HF_API = "https://router.huggingface.co/hf-inference/models/"

def _post(model_id: str, payload: dict, timeout: int = 90):
    token = os.getenv("HF_TOKEN", "")
    headers = {"Accept": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    # ✅ 모델 로딩 기다리기
    payload = {**payload, "options": {"wait_for_model": True}}

    r = requests.post(f"{HF_API}{model_id}", headers=headers, json=payload, timeout=timeout)

    if r.status_code == 503:
        return None, "모델 로딩 중입니다. 잠시 후 다시 시도해 주세요."
    if r.status_code >= 400:
        try:
            err = r.json()
        except Exception:
            err = r.text
        return None, f"모델 호출 실패 ({r.status_code}): {err}"

    return r.json(), None

def summarize(text: str):
    model = "sshleifer/distilbart-cnn-12-6"
    data, err = _post(model, {
        "inputs": text,
        "parameters": {"max_length": 120, "min_length": 25, "do_sample": False}
    }, timeout=60)
    if err:
        return None, err
    try:
        return data[0].get("summary_text", "").strip(), None
    except Exception:
        return None, f"요약 실패: {data}"

def translate_en_to_ko(text: str):
    # ✅ mBART 번역 모델
    model = "facebook/mbart-large-50-many-to-many-mmt"
    
    data, err = _post(model, {
        "inputs": text,  # 프롬프트 제거
        "parameters": {
            "src_lang": "en_XX",  # 영어
            "tgt_lang": "ko_KR"   # 한국어
        }
    }, timeout=60)
    
    print(f"[DEBUG] translate data: {data}")
    
    if err:
        return None, err
    try:
        if isinstance(data, list) and len(data) > 0:
            result = data[0].get("translation_text", "")
            return result.strip(), None
        return None, f"번역 실패: {data}"
    except Exception as e:
        return None, f"번역 실패: {e} - {data}"
    

def generate_text(prompt: str):
    model = "sshleifer/distilbart-cnn-12-6"
    full_text = f"{prompt}"
    
    data, err = _post(model, {
        "inputs": full_text,
        "parameters": {
            "max_length": 100,
            "min_length": 50,
            "do_sample": True,
            "temperature": 0.9
        }
    }, timeout=90)
    
    print(f"[DEBUG] generate data: {data}")
    
    if err:
        return None, err
    
    try:
        # summarize와 같은 구조
        result = data[0].get("summary_text", "").strip()
        return result, None
    except Exception as e:
        return None, f"생성 실패: {e} - {data}"