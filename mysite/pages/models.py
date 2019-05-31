from django.forms import Form, CharField, EmailField, TextInput, PasswordInput, EmailInput

# Create your models here.

class RegisterForm(Form):
    username = CharField(widget=TextInput(attrs={'class': 'form-control'}))
    email = EmailField(widget=EmailInput(attrs={'class': 'form-control'}))
    email_repeat = EmailField(widget=EmailInput(attrs={'class': 'form-control'}))
    password = CharField(widget=PasswordInput(attrs={'class': 'form-control'}))
    password_repeat = CharField(widget=PasswordInput(attrs={'class': 'form-control'}))

class LoginForm(Form):
    username = CharField(widget=TextInput(attrs={'class': 'form-control'}))
    password = CharField(widget=PasswordInput(attrs={'class': 'form-control'}))