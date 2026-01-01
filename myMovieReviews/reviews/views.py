from django.shortcuts import render, redirect, get_object_or_404

from .models import Review

def review_list(request):
    reviews = Review.objects.all()
    context = {
        'reviews': reviews
    }
    return render(request, 'reviews/review_list.html', context)

def review_detail(request, pk):
    review = get_object_or_404(Review, id=pk)
    context = {
        'review': review
    }
    return render(request, 'reviews/review_detail.html', context)

def review_create(request):
    if request.method == 'POST':
        Review.objects.create(
            title=request.POST['title'],
            release_year=request.POST['release_year'],
            genre=request.POST['genre'],
            rating=request.POST['rating'],
            director=request.POST['director'],
            main_actor=request.POST['main_actor'],
            runtime=request.POST['runtime'],
            review_content=request.POST['review_content'],
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
