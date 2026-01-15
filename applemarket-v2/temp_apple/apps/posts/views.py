from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Post
from .forms import PostForm
from .services.ocr_service import NutritionOCRService
import os
import tempfile

# Create your views here.
def main(request):
    posts = Post.objects.all()

    search_txt = request.GET.get('search_txt')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')

    if search_txt:
        posts = posts.filter(title__icontains=search_txt)
    
    try:
        if min_price:
            posts = posts.filter(price__gte=int(min_price))
        if max_price:
            posts = posts.filter(price__lte=int(max_price))
    except (ValueError, TypeError):
        pass

    context = {
        'posts': posts,
        'search_txt': search_txt,
        'min_price': min_price,
        'max_price': max_price,
    }
    return render(request, 'posts/list.html', context=context)

def create(request):
    if request.method == 'GET':
        form = PostForm()
        context = { 'form': form }
        return render(request, 'posts/create.html', context=context)
    else:
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
        return redirect('/')

def detail(request, pk):
    target_post = Post.objects.get(id = pk)
    context = { 'post': target_post }
    return render(request, 'posts/detail.html', context=context)

def update(request, pk):
    post = Post.objects.get(id=pk)
    if request.method == 'GET':
        form = PostForm(instance=post)
        context = {
            'form': form, 
            'post': post
        }
        return render(request, 'posts/update.html', context=context)
    else:
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
        return redirect('posts:detail', pk=pk)

def delete(request, pk):
    post = Post.objects.get(id=pk)
    post.delete()
    return redirect('/')


# OCR 분석 API (새로 추가)
@require_POST
def analyze_nutrition(request):
    if 'nutrition_image' not in request.FILES:
        return JsonResponse({'error': '이미지가 없습니다.'}, status=400)

    nutrition_image = request.FILES['nutrition_image']

    ext = os.path.splitext(nutrition_image.name)[1].lower()
    if ext not in [".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tif", ".tiff"]:
        ext = ".png"

    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=ext)
    try:
        for chunk in nutrition_image.chunks():
            tmp.write(chunk)
        tmp.close()

        ocr_service = NutritionOCRService()
        nutrition_info = ocr_service.analyze_nutrition_label(tmp.name)
        return JsonResponse(nutrition_info)

    except Exception as e:
        print(f"OCR 분석 오류: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)

    finally:
        try:
            if tmp and os.path.exists(tmp.name):
                os.remove(tmp.name)
        except:
            pass