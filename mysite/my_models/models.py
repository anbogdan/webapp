from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Flavor(models.Model):
    flv_id = models.CharField(max_length=36)
    name = models.CharField(max_length=20)
    ram = models.FloatField()
    vcpu = models.IntegerField()
    disk = models.IntegerField()

    def __str__(self):
        return self.name

class Application(models.Model):
    name = models.CharField(max_length=20)
    flv = models.CharField(max_length=20)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    allocated = models.BooleanField()
    ip = models.CharField(max_length=15)
    repo = models.CharField(max_length=100)
    status = models.CharField(max_length=20)
    action = models.CharField(max_length=20)

class SshKey(models.Model):
    sshkey = models.CharField(max_length=1024)
    user = models.ForeignKey(User, on_delete=models.CASCADE)