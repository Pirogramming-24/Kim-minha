import os
import requests
from dotenv import load_dotenv

load_dotenv()

class TMDBService:
    BASE_URL = "https://api.themoviedb.org/3"
    IMAGE_BASE_URL = "https://image.tmdb.org/t/p/w500"
    
    def __init__(self):
        self.api_key = os.getenv('TMDB_API_KEY')
    
    def get_popular_movies(self, page=1):
        """인기 영화 목록 가져오기"""
        url = f"{self.BASE_URL}/movie/popular"
        params = {
            'api_key': self.api_key,
            'language': 'ko-KR',
            'page': page
        }
        response = requests.get(url, params=params)
        if response.status_code == 200:
            return response.json()
        return None
    
    def get_movie_detail(self, movie_id):
        """영화 상세 정보 가져오기"""
        url = f"{self.BASE_URL}/movie/{movie_id}"
        params = {
            'api_key': self.api_key,
            'language': 'ko-KR',
            'append_to_response': 'credits'
        }
        response = requests.get(url, params=params)
        if response.status_code == 200:
            return response.json()
        return None
    
    def search_movies(self, query):
        """영화 검색"""
        url = f"{self.BASE_URL}/search/movie"
        params = {
            'api_key': self.api_key,
            'language': 'ko-KR',
            'query': query
        }
        response = requests.get(url, params=params)
        if response.status_code == 200:
            return response.json()
        return None
    
    def get_poster_url(self, poster_path):
        """포스터 이미지 URL 반환"""
        if poster_path:
            return f"{self.IMAGE_BASE_URL}{poster_path}"
        return None