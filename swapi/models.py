from fileinput import filename

from django.db import models

# Create your models here.
class File(models.Model):
    filename = models.CharField(max_length=40, unique=True)
    datetime = models.DateTimeField(auto_now_add=True)
    count_of_people = models.IntegerField()