from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.
class User(AbstractUser):
    nickname = models.CharField(max_length=100)
    image = models.ImageField(upload_to="user",null = True)
    image_data = models.CharField(max_length=3000,null = True)
    face_registered = models.BooleanField(default=False)
    mode = models.CharField(max_length=100,default = "normal")
