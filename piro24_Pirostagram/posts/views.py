from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView

from .models import Post, Follow, Like, Comment, Story, StoryItem
from .forms import PostForm, CommentForm, StoryUploadForm



class FeedView(LoginRequiredMixin, ListView):
    model = Post
    template_name = "posts/feed.html"
    context_object_name = "posts"

    def get_queryset(self):
        me = self.request.user
        following_ids = Follow.objects.filter(from_user=me).values_list("to_user_id", flat=True)
        qs = (
            Post.objects.filter(author_id__in=list(following_ids) + [me.id])
            .select_related("author")
            .annotate(
                likes_count=Count("likes", distinct=True),
                comments_count=Count("comments", distinct=True),
            )
        )
        return qs

    from .models import Story

User = get_user_model()

def get_context_data(self, **kwargs):
    ctx = super().get_context_data(**kwargs)
    me = self.request.user

    # 내 최신 스토리(있으면 내 동그라미 클릭시 스토리로)
    ctx["my_latest_story"] = Story.objects.filter(user=me).order_by("-created_at").first()

    # 모든 유저 목록(나 제외)
    users = list(User.objects.exclude(id=me.id).order_by("username"))

    # 유저별 최신 스토리 id 만들기 (N+1 피하려고 Story 전체 한번만 훑음)
    latest_story_by_user = {}
    for s in Story.objects.select_related("user").order_by("-created_at"):
        if s.user_id not in latest_story_by_user:
            latest_story_by_user[s.user_id] = s.id

    # 템플릿에서 쓰기 편하게 묶어서 내려줌
    story_profiles = []
    for u in users:
        story_profiles.append({
            "user": u,
            "story_id": latest_story_by_user.get(u.id)  # 없으면 None
        })

    ctx["story_profiles"] = story_profiles
    return ctx
class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = "posts/post_form.html"
    success_url = reverse_lazy("posts:feed")

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class PostOwnerMixin(UserPassesTestMixin):
    def test_func(self):
        return self.get_object().author == self.request.user


class PostUpdateView(LoginRequiredMixin, PostOwnerMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = "posts/post_form.html"
    success_url = reverse_lazy("posts:feed")


class PostDeleteView(LoginRequiredMixin, PostOwnerMixin, DeleteView):
    model = Post
    template_name = "posts/post_confirm_delete.html"
    success_url = reverse_lazy("posts:feed")


@login_required
def profile_view(request, username):
    User = get_user_model()
    target = get_object_or_404(User, username=username)

    is_following = Follow.objects.filter(from_user=request.user, to_user=target).exists()
    followers_count = Follow.objects.filter(to_user=target).count()
    following_count = Follow.objects.filter(from_user=target).count()
    latest_story = Story.objects.filter(user=target).order_by("-created_at").first()


    posts = (
        Post.objects.filter(author=target)
        .select_related("author")
        .annotate(
            likes_count=Count("likes", distinct=True),
            comments_count=Count("comments", distinct=True),
        )
    )

    return render(
        request,
        "posts/profile.html",
        {
            "target": target,
            "is_following": is_following,
            "followers_count": followers_count,
            "following_count": following_count,
            "posts": posts,
            "latest_story": latest_story,

        },
    )


@login_required
def follow_toggle(request, username):
    if request.method != "POST":
        return redirect("posts:profile", username=username)

    User = get_user_model()
    target = get_object_or_404(User, username=username)

    if target == request.user:
        return redirect("posts:profile", username=username)

    rel = Follow.objects.filter(from_user=request.user, to_user=target)
    if rel.exists():
        rel.delete()
    else:
        Follow.objects.create(from_user=request.user, to_user=target)

    return redirect("posts:profile", username=username)


@login_required
def like_toggle(request, pk):
    if request.method != "POST":
        return redirect("posts:detail", pk=pk)

    post = get_object_or_404(Post, pk=pk)
    obj = Like.objects.filter(user=request.user, post=post)
    if obj.exists():
        obj.delete()
    else:
        Like.objects.create(user=request.user, post=post)

    next_url = request.POST.get("next")
    if next_url:
        return redirect(next_url)
    return redirect("posts:detail", pk=pk)


@login_required
def post_detail(request, pk):
    post = get_object_or_404(Post.objects.select_related("author"), pk=pk)
    comments = post.comments.select_related("user").all()
    liked = Like.objects.filter(user=request.user, post=post).exists()

    return render(
        request,
        "posts/detail.html",
        {
            "post": post,
            "comments": comments,
            "comment_form": CommentForm(),
            "liked": liked,
            "likes_count": post.likes.count(),
        },
    )


@login_required
def comment_create(request, pk):
    if request.method != "POST":
        return redirect("posts:detail", pk=pk)

    post = get_object_or_404(Post, pk=pk)
    form = CommentForm(request.POST)
    if form.is_valid():
        Comment.objects.create(
            post=post,
            user=request.user,
            content=form.cleaned_data["content"],
        )
    return redirect("posts:detail", pk=pk)


@login_required
def comment_update(request, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id)
    if comment.user != request.user:
        return redirect("posts:detail", pk=comment.post_id)

    if request.method == "POST":
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            return redirect("posts:detail", pk=comment.post_id)
    else:
        form = CommentForm(instance=comment)

    return render(request, "posts/comment_form.html", {"form": form, "comment": comment})


@login_required
def comment_delete(request, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id)
    if comment.user != request.user:
        return redirect("posts:detail", pk=comment.post_id)

    post_id = comment.post_id
    if request.method == "POST":
        comment.delete()
        return redirect("posts:detail", pk=post_id)

    return render(request, "posts/comment_confirm_delete.html", {"comment": comment})


@login_required
def story_create(request):
    if request.method == "POST":
        images = request.FILES.getlist("images")
        if images:
            story = Story.objects.create(user=request.user)
            for idx, img in enumerate(images):
                StoryItem.objects.create(story=story, image=img, order=idx)
            return redirect("posts:story_view", story_id=story.id)

    return render(request, "posts/story_create.html")


def story_view(request, story_id):
    story = get_object_or_404(Story.objects.select_related("user"), id=story_id)

    items = list(StoryItem.objects.filter(story=story).order_by("order", "id"))
    if not items:
        return redirect("posts:feed")

    # 현재 사진 인덱스
    try:
        i = int(request.GET.get("i", 0))
    except ValueError:
        i = 0
    if i < 0:
        i = 0
    if i >= len(items):
        i = len(items) - 1

    item = items[i]

    # 스토리 전체 순서(스토리 id 기준)로 prev/next 스토리 결정
    story_ids = list(Story.objects.order_by("id").values_list("id", flat=True))
    cur_idx = story_ids.index(story.id)
    prev_story_id = story_ids[cur_idx - 1] if cur_idx > 0 else None
    next_story_id = story_ids[cur_idx + 1] if cur_idx < len(story_ids) - 1 else None

    # 이전/다음 URL 만들기
    if i > 0:
        prev_url = f"/stories/{story.id}/?i={i-1}"
    else:
        if prev_story_id:
            prev_count = StoryItem.objects.filter(story_id=prev_story_id).count()
            prev_last = prev_count - 1 if prev_count > 0 else 0
            prev_url = f"/stories/{prev_story_id}/?i={prev_last}"
        else:
            prev_url = None

    if i < len(items) - 1:
        next_url = f"/stories/{story.id}/?i={i+1}"
    else:
        if next_story_id:
            next_url = f"/stories/{next_story_id}/?i=0"
        else:
            next_url = None

    return render(request, "posts/story_view.html", {
        "story": story,
        "item": item,
        "prev_url": prev_url,
        "next_url": next_url,
    })

@login_required
def user_search(request):
    q = (request.GET.get("q") or "").strip()
    User = get_user_model()

    results = []
    if q:
        results = User.objects.filter(
            Q(username__icontains=q) | Q(first_name__icontains=q) | Q(last_name__icontains=q)
        ).order_by("username")[:30]

    return render(request, "posts/user_search.html", {"q": q, "results": results})
