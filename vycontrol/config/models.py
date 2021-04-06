from django.db import models
from django.contrib.auth.models import Group
from django.contrib.auth.models import User

class Instance(models.Model):
    hostname = models.CharField(max_length=120, primary_key=True)
    alias = models.CharField(max_length=30)
    port = models.IntegerField()
    key = models.CharField(max_length=100)
    https = models.BooleanField()
    main = models.BooleanField(default=False)
    group = models.ForeignKey(Group, null=True, on_delete=models.SET_NULL)

    
Group.add_to_class('active', models.BooleanField(default=True))
