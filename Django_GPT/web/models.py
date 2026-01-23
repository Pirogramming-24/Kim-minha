from django.db import models
from django.conf import settings

class ChatMessage(models.Model):
    TAB_CHOICES = [
        ("summarize", "summarize"),
        ("translate", "translate"),
        ("generate", "generate"),
    ]
    ROLE_CHOICES = [
        ("user", "user"),
        ("assistant", "assistant"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    tab = models.CharField(max_length=20, choices=TAB_CHOICES)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]