from django.shortcuts import render, redirect
from .decorators import login_required_with_alert
from .models import ChatMessage
from . import hf_client

def home(request):
    return redirect("summarize")

def _load_messages(user, tab, limit=40):
    return ChatMessage.objects.filter(user=user, tab=tab).order_by("-created_at")[:limit][::-1]

def _save_pair(user, tab, user_text, assistant_text):
    ChatMessage.objects.create(user=user, tab=tab, role="user", content=user_text)
    ChatMessage.objects.create(user=user, tab=tab, role="assistant", content=assistant_text)

# 공개 탭: 비로그인 허용 (저장 안 함)
def summarize(request):
    tab = "summarize"
    messages = _load_messages(request.user, tab) if request.user.is_authenticated else []

    if request.method == "POST":
        prompt = (request.POST.get("prompt") or "").strip()
        if not prompt:
            return render(request, "web/chat_page.html", {
                "page_title": "요약",
                "active_tab": tab,
                "messages": messages,
                "error": "입력이 비어있습니다.",
            })

        result, err = hf_client.summarize(prompt)
        if err:
            return render(request, "web/chat_page.html", {
                "page_title": "요약",
                "active_tab": tab,
                "messages": messages,
                "one_shot_user": prompt if not request.user.is_authenticated else None,
                "error": err,
            })

        if request.user.is_authenticated:
            _save_pair(request.user, tab, prompt, result)
            messages = _load_messages(request.user, tab)
            return render(request, "web/chat_page.html", {
                "page_title": "요약",
                "active_tab": tab,
                "messages": messages,
            })

        # 비로그인: 저장 안 함 → 새로고침(F5)하면 초기화
        return render(request, "web/chat_page.html", {
            "page_title": "요약",
            "active_tab": tab,
            "messages": [],
            "one_shot_user": prompt,
            "one_shot_assistant": result,
        })

    return render(request, "web/chat_page.html", {
        "page_title": "요약",
        "active_tab": tab,
        "messages": messages,
    })

# 제한 탭: 로그인 필요
@login_required_with_alert
def translate(request):
    tab = "translate"
    messages = _load_messages(request.user, tab)

    if request.method == "POST":
        prompt = (request.POST.get("prompt") or "").strip()
        if not prompt:
            return render(request, "web/chat_page.html", {
                "page_title": "번역",
                "active_tab": tab,
                "messages": messages,
                "error": "입력이 비어있습니다.",
            })

        result, err = hf_client.translate_en_to_ko(prompt)
        if err:
            return render(request, "web/chat_page.html", {
                "page_title": "번역",
                "active_tab": tab,
                "messages": messages,
                "error": err,
            })

        _save_pair(request.user, tab, prompt, result)
        messages = _load_messages(request.user, tab)

    return render(request, "web/chat_page.html", {
        "page_title": "번역",
        "active_tab": tab,
        "messages": messages,
    })

@login_required_with_alert
def generate(request):
    tab = "generate"
    messages = _load_messages(request.user, tab)

    if request.method == "POST":
        prompt = (request.POST.get("prompt") or "").strip()
        if not prompt:
            return render(request, "web/chat_page.html", {
                "page_title": "글생성",
                "active_tab": tab,
                "messages": messages,
                "error": "입력이 비어있습니다.",
            })

        result, err = hf_client.generate_text(prompt)
        if err:
            return render(request, "web/chat_page.html", {
                "page_title": "글생성",
                "active_tab": tab,
                "messages": messages,
                "error": err,
            })

        _save_pair(request.user, tab, prompt, result)
        messages = _load_messages(request.user, tab)

    return render(request, "web/chat_page.html", {
        "page_title": "글생성",
        "active_tab": tab,
        "messages": messages,
    })