from django.forms import Form, CharField, TextInput


# Create your models here.

class AllocateAppForm(Form):
    flavor_name = CharField(widget=TextInput)
    server_name = CharField(widget=TextInput)