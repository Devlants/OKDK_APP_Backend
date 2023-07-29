from django.db import models

class Brand(models.Model):
    name = models.CharField(max_length=100)
    api = models.URLField(max_length=100)


