from django import forms
from .models import Post

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = [
            'title', 
            'content', 
            'region', 
            'user', 
            'price', 
            'photo',
            'nutrition_image',
            'calories',
            'carbohydrates',
            'protein',
            'fat'
        ]
        widgets = {
            'calories': forms.NumberInput(attrs={'step': '0.1','placeholder': '이미지 업로드 시 자동 입력'}),
            'carbohydrates': forms.NumberInput(attrs={'step': '0.1', 'placeholder': '이미지 업로드 시 자동 입력'}),
            'protein': forms.NumberInput(attrs={'step': '0.1', 'placeholder': '이미지 업로드 시 자동 입력'}),
            'fat': forms.NumberInput(attrs={'step': '0.1', 'placeholder': '이미지 업로드 시 자동 입력'}),
        }