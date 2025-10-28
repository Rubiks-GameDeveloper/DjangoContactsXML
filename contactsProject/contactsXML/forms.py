from django import forms

class ContactForm(forms.Form):
    first_name = forms.CharField(max_length=100, label="Имя")
    last_name = forms.CharField(max_length=100, label="Фамилия")
    email = forms.EmailField(label="Email")
    phone = forms.CharField(max_length=20, label="Телефон")

class UploadFileForm(forms.Form):
    file = forms.FileField(label="Выберите XML-файл")