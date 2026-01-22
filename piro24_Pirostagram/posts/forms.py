from django import forms
from .models import Post, Comment

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ["image", "content"]

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["content"]

class MultiFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True

class StoryUploadForm(forms.Form):
    images = forms.ImageField(widget=MultiFileInput(attrs={"multiple": True}))
