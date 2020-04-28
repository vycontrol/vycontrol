from django.db import models


class Instance(models.Model):
    hostname = models.CharField(max_length=120, primary_key=True)
    alias = models.CharField(max_length=30)
    port = models.IntegerField()
    key = models.CharField(max_length=100)
    https = models.BooleanField()
    main = models.BooleanField(default=False)
    


