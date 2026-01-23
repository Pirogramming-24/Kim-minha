import requests
from django.conf import settings

HF_API = "https://api-inference.huggingface.co/models/"

def _post(model_id: str, payload: dict, timeout: int = 90):
    token = getattr(settings, "HF_TOKEN", "")
    headers = {"Accept": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    # 모델 로딩 대기
    payload = {**payload, "options": {"wait_for_model": True}}

    r = requests.post(f"{HF_API}{model_id}", headers=headers, json=payload, timeout=timeout)

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
        return None, f"요약 파싱 실패: {data}"

def translate_en_to_ko(text: str):
    model = "Helsinki-NLP/opus-mt-en-ko"
    data, err = _post(model, {"inputs": text}, timeout=60)
    if err:
        return None, err
    try:
        return data[0].get("translation_text", "").strip(), None
    except Exception:
        return None, f"번역 파싱 실패: {data}"

def generate_text(prompt: str):
    model = "Qwen/Qwen2.5-1.5B-Instruct"
    data, err = _post(model, {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 220,
            "temperature": 0.7,
            "return_full_text": False
        }
    }, timeout=120)
    if err:
        return None, err

    # 모델마다 응답 형태가 달라서 방어적으로 처리
    if isinstance(data, list) and data:
        if "generated_text" in data[0]:
            return str(data[0]["generated_text"]).strip(), None
    if isinstance(data, dict) and "generated_text" in data:
        return str(data["generated_text"]).strip(), None

    return str(data).strip(), None