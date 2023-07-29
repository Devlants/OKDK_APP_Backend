from django.db import models

class Favorite(models.Model):
    user = models.ForeignKey("account.User",on_delete=models.CASCADE)
    brand = models.ForeignKey("coffee.Brand",on_delete=models.CASCADE)
    menu = models.IntegerField()
    temperature = models.IntegerField()
    size = models.IntegerField()

