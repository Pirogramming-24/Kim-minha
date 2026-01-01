from django.db import models

# Create your models here.

class Review(models.Model):
    title = models.CharField(max_length=100, verbose_name='제목')
    release_year = models.IntegerField(verbose_name='개봉년도')
    genre = models.CharField(max_length=50, verbose_name='장르')
    rating = models.DecimalField(max_digits=2, decimal_places=1, verbose_name='별점')
    director = models.CharField(max_length=100, verbose_name='감독')
    main_actor = models.CharField(max_length=200, verbose_name='주연')
    runtime = models.IntegerField(verbose_name='러닝타임(분)')
    review_content = models.TextField(verbose_name='리뷰')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='작성일')

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created_at']
