from django.db import models
from django.contrib.auth.models import User
from django.forms import Form, CharField, ModelMultipleChoiceField, URLField, TextInput, URLInput


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
    repo = models.URLField()
    status = models.CharField(max_length=10)

class AddAppForm(Form):
    name = CharField(widget=TextInput(attrs={'class': 'form-control'}))
    flv = ModelMultipleChoiceField(queryset=Flavor.objects.all())
    repo = URLField(widget=URLInput)