from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.http import JsonResponse
from .models import Review
from .services.tmdb_service import TMDBService
from .services.chatbot_service import ChatbotService
import json

tmdb = TMDBService()
chatbot = ChatbotService()

def review_list(request):
    # 정렬 파라미터
    sort = request.GET.get('sort', '-created_at')
    
    reviews = Review.objects.all().order_by(sort)
    
    # 페이지네이션
    paginator = Paginator(reviews, 100)  # 많이 보여주기
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    # TMDB 인기 영화 가져오기
    tmdb_movies = tmdb.get_popular_movies()
    tmdb_results = tmdb_movies.get('results', []) if tmdb_movies else []
    
    # 총 개수 계산
    total_count = len(tmdb_results) + reviews.count()
    
    context = {
        'reviews': page_obj,
        'tmdb_movies': tmdb_results,
        'page_obj': page_obj,
        'total_count': total_count,
    }
    return render(request, 'reviews/review_list.html', context)

def review_detail(request, pk):
    review = get_object_or_404(Review, id=pk)
    
    # TMDB 상세 정보 가져오기
    tmdb_detail = None
    if review.tmdb_id:
        tmdb_detail = tmdb.get_movie_detail(review.tmdb_id)
    
    context = {
        'review': review,
        'tmdb_detail': tmdb_detail,
        'poster_url': tmdb.get_poster_url(review.poster_path) if review.poster_path else None
    }
    return render(request, 'reviews/review_detail.html', context)

def review_create(request):
    if request.method == 'POST':
        tmdb_id = request.POST.get('tmdb_id')
        poster_path = request.POST.get('poster_path')
        poster_image = request.FILES.get('poster_image')  # 파일 가져오기
        
        review = Review.objects.create(
            title=request.POST['title'],
            release_year=request.POST['release_year'],
            genre=request.POST['genre'],
            rating=request.POST['rating'],
            director=request.POST['director'],
            main_actor=request.POST['main_actor'],
            runtime=request.POST['runtime'],
            review_content=request.POST['review_content'],
            tmdb_id=int(tmdb_id) if tmdb_id else None,
            poster_path=poster_path if poster_path else None,
            poster_image=poster_image if poster_image else None,  # 이미지 저장
        )
        return redirect('reviews:review_list')
    
    return render(request, 'reviews/review_form.html')

def review_update(request, pk):
    review = get_object_or_404(Review, id=pk)
    
    if request.method == 'POST':
        review.title = request.POST['title']
        review.release_year = request.POST['release_year']
        review.genre = request.POST['genre']
        review.rating = request.POST['rating']
        review.director = request.POST['director']
        review.main_actor = request.POST['main_actor']
        review.runtime = request.POST['runtime']
        review.review_content = request.POST['review_content']
        
        # 새 이미지가 업로드되었다면 교체
        poster_image = request.FILES.get('poster_image')
        if poster_image:
            review.poster_image = poster_image
        
        review.save()
        return redirect('reviews:review_detail', pk=pk)
    
    context = {
        'review': review
    }
    return render(request, 'reviews/review_form.html', context)

def review_delete(request, pk):
    if request.method == 'POST':
        review = get_object_or_404(Review, id=pk)
        review.delete()
    return redirect('reviews:review_list')

def search_movies(request):
    query = request.GET.get('q', '')
    results = []
    
    if query:
        # DB에서 검색
        db_results = Review.objects.filter(
            title__icontains=query
        ) | Review.objects.filter(
            director__icontains=query
        ) | Review.objects.filter(
            main_actor__icontains=query
        )
        
        # TMDB에서 검색
        tmdb_results = tmdb.search_movies(query)
        
        context = {
            'query': query,
            'db_results': db_results,
            'tmdb_results': tmdb_results.get('results', []) if tmdb_results else [],
        }
        return render(request, 'reviews/search_results.html', context)
    
    return redirect('reviews:review_list')

def tmdb_import(request, tmdb_id):
    """TMDB 영화를 리뷰로 가져오기"""
    movie = tmdb.get_movie_detail(tmdb_id)
    
    if movie:
        # 감독 찾기
        director = '정보없음'
        if 'credits' in movie and 'crew' in movie['credits']:
            for crew in movie['credits']['crew']:
                if crew['job'] == 'Director':
                    director = crew['name']
                    break
        
        # 주연 배우 찾기
        actors = []
        if 'credits' in movie and 'cast' in movie['credits']:
            actors = [cast['name'] for cast in movie['credits']['cast'][:3]]
        main_actor = ', '.join(actors) if actors else '정보없음'
        
        # 장르
        genres = [g['name'] for g in movie.get('genres', [])]
        genre = ', '.join(genres) if genres else '기타'
        
        context = {
            'tmdb_movie': movie,
            'director': director,
            'main_actor': main_actor,
            'genre': genre,
            'poster_path': movie.get('poster_path'),
            'tmdb_id': tmdb_id,
        }
        return render(request, 'reviews/review_form.html', context)
    
    return redirect('reviews:review_list')

def chatbot_page(request):
    """AI 챗봇 페이지"""
    return render(request, 'reviews/chatbot.html')

def chatbot_api(request):
    """챗봇 API 엔드포인트"""
    if request.method == 'POST':
        data = json.loads(request.body)
        user_message = data.get('message', '')
        conversation_history = data.get('history', [])
        
        response = chatbot.chat(user_message, conversation_history)
        
        return JsonResponse({
            'response': response,
            'status': 'success'
        })
    
    return JsonResponse({'error': 'Invalid request'}, status=400)