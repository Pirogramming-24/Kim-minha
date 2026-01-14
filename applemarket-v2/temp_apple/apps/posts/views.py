from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Post
from .forms import PostForm
from .services.ocr_service import NutritionOCRService
import os

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
    """영양성분표 이미지 OCR 분석 API"""
    if 'nutrition_image' not in request.FILES:
        return JsonResponse({'error': '이미지가 없습니다.'}, status=400)
    
    nutrition_image = request.FILES['nutrition_image']
    
    # 임시 파일로 저장
    temp_path = f'/tmp/{nutrition_image.name}'
    with open(temp_path, 'wb+') as destination:
        for chunk in nutrition_image.chunks():
            destination.write(chunk)
    
    try:
        # OCR 분석
        ocr_service = NutritionOCRService()
        nutrition_info = ocr_service.analyze_nutrition_label(temp_path)

        # mapped = {
        #  "calories": nutrition_info.get("calories_kcal"),
        #  "carbohydrates": nutrition_info.get("carbohydrates_g"),
        #  "protein": nutrition_info.get("protein_g"),
        #  "fat": nutrition_info.get("fat_g"),}
        
        # 임시 파일 삭제
        if os.path.exists(temp_path):
            os.remove(temp_path)
        
        return JsonResponse(nutrition_info)
    
    except Exception as e:
        print(f"OCR 분석 오류: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)