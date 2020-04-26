from django.db import models


class Instance(models.Model):
    alias = models.CharField(max_length=30)
    hostname = models.CharField(max_length=120)
    port = models.IntegerField()
    key = models.CharField(max_length=100)
    https = models.BooleanField()



