from django.db import models

# Create your models here.

class DevTool(models.Model): #대소문자 구분해서 쓰쟈
    name= models.CharField(max_length=50)
    kind= models.CharField(max_length=50)
    content= models.TextField()

    created_at=models.DateTimeField(auto_now_add=True) #생성 시간 stamp

    def __str__(self):
        return self.name
    
class Idea(models.Model):
    title = models.CharField(max_length=100)
    image = models.ImageField(upload_to="ideas/", blank=True, null=True)
    content = models.TextField()
    interest = models.IntegerField(default=0)

    devtool = models.ForeignKey(
        DevTool,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="ideas",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class IdeaStar(models.Model):
    idea = models.ForeignKey(Idea, on_delete=models.CASCADE, related_name="stars")
    session_key = models.CharField(max_length=40, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["idea", "session_key"], name="unique_star_per_session")
        ]