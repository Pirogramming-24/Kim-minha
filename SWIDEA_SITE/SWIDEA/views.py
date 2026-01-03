from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.db.models import Count

from .models import Idea, DevTool, IdeaStar


def _get_session_key(request):
    if not request.session.session_key:
        request.session.save()
    return request.session.session_key


def idea_list(request):
    sort = request.GET.get("sort", "latest")

    qs = (
        Idea.objects.select_related("devtool")
        .annotate(star_count=Count("stars"))
    )

    if sort == "stars":
        qs = qs.order_by("-star_count", "-created_at")
    elif sort == "name":
        qs = qs.order_by("title", "-created_at")
    elif sort == "oldest":
        qs = qs.order_by("created_at")
    elif sort == "interest":
        qs = qs.order_by("-interest", "-created_at")
    else:  # latest
        qs = qs.order_by("-created_at")

    session_key = _get_session_key(request)
    starred_ids = set(
        IdeaStar.objects.filter(session_key=session_key).values_list("idea_id", flat=True)
    )

    context = {
        "ideas": qs,
        "sort": sort,
        "starred_ids": starred_ids,
    }
    return render(request, "SWIDEA/idea_list.html", context)


def idea_create(request):
    devtools = DevTool.objects.all().order_by("name")

    if request.method == "POST":
        title = request.POST.get("title", "").strip()
        content = request.POST.get("content", "")
        interest = int(request.POST.get("interest") or 0)
        devtool_id = request.POST.get("devtool") or None
        image = request.FILES.get("image")

        devtool = DevTool.objects.filter(id=devtool_id).first() if devtool_id else None

        Idea.objects.create(
            title=title,
            content=content,
            interest=interest,
            devtool=devtool,
            image=image,
        )
        return redirect("swidea:idea_list")

    return render(request, "SWIDEA/idea_form.html", {"devtools": devtools, "mode": "create"})


def idea_detail(request, pk):
    idea = get_object_or_404(Idea.objects.select_related("devtool"), id=pk)
    session_key = _get_session_key(request)
    is_starred = IdeaStar.objects.filter(idea=idea, session_key=session_key).exists()
    star_count = idea.stars.count()

    return render(
        request,
        "SWIDEA/idea_detail.html",
        {"idea": idea, "is_starred": is_starred, "star_count": star_count},
    )


def idea_update(request, pk):
    idea = get_object_or_404(Idea, id=pk)
    devtools = DevTool.objects.all().order_by("name")

    if request.method == "POST":
        idea.title = request.POST.get("title", "").strip()
        idea.content = request.POST.get("content", "")
        idea.interest = int(request.POST.get("interest") or 0)

        devtool_id = request.POST.get("devtool") or None
        idea.devtool = DevTool.objects.filter(id=devtool_id).first() if devtool_id else None

        if request.FILES.get("image"):
            idea.image = request.FILES.get("image")

        idea.save()
        return redirect("swidea:idea_detail", pk=idea.id)

    return render(
        request,
        "SWIDEA/idea_form.html",
        {"idea": idea, "devtools": devtools, "mode": "update"},
    )


def idea_delete(request, pk):
    idea = get_object_or_404(Idea, id=pk)
    if request.method == "POST":
        idea.delete()
    return redirect("swidea:idea_list")


def idea_toggle_star(request, pk):
    idea = get_object_or_404(Idea, id=pk)
    session_key = _get_session_key(request)

    if request.method == "POST":
        star = IdeaStar.objects.filter(idea=idea, session_key=session_key)
        if star.exists():
            star.delete()
        else:
            IdeaStar.objects.create(idea=idea, session_key=session_key)

    return redirect(request.META.get("HTTP_REFERER", "/"))


def idea_interest_plus(request, pk):
    return _idea_interest_change(request, pk, delta=1)


def idea_interest_minus(request, pk):
    return _idea_interest_change(request, pk, delta=-1)


def _idea_interest_change(request, pk, delta):
    idea = get_object_or_404(Idea, id=pk)

    if request.method == "POST":
        idea.interest = max(0, idea.interest + delta)
        idea.save()

        # AJAX면 JSON으로 숫자만 반환
        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JsonResponse({"interest": idea.interest})

    return redirect(request.META.get("HTTP_REFERER", "/"))


def devtool_list(request):
    devtools = DevTool.objects.all().order_by("name")
    return render(request, "SWIDEA/devtool_list.html", {"devtools": devtools})


def devtool_create(request):
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        kind = request.POST.get("kind", "").strip()
        content = request.POST.get("content", "")

        DevTool.objects.create(name=name, kind=kind, content=content)
        return redirect("swidea:devtool_list")

    return render(request, "SWIDEA/devtool_form.html", {"mode": "create"})


def devtool_detail(request, pk):
    devtool = get_object_or_404(DevTool, id=pk)
    ideas = devtool.ideas.all().order_by("-created_at")
    return render(request, "SWIDEA/devtool_detail.html", {"devtool": devtool, "ideas": ideas})


def devtool_update(request, pk):
    devtool = get_object_or_404(DevTool, id=pk)

    if request.method == "POST":
        devtool.name = request.POST.get("name", "").strip()
        devtool.kind = request.POST.get("kind", "").strip()
        devtool.content = request.POST.get("content", "")
        devtool.save()
        return redirect("swidea:devtool_detail", pk=devtool.id)

    return render(request, "SWIDEA/devtool_form.html", {"devtool": devtool, "mode": "update"})


def devtool_delete(request, pk):
    devtool = get_object_or_404(DevTool, id=pk)
    if request.method == "POST":
        devtool.delete()
    return redirect("swidea:devtool_list")

