# contactsXML/forms.py
from django import forms
from django.core.validators import RegexValidator

from django import forms
from django.core.validators import RegexValidator

class ContactForm(forms.Form):

    # Только кириллица, минимум 2 буквы
    name_validator = RegexValidator(
        regex=r'^[А-ЯЁа-яё]{2,}$',
        message="Поле должно содержать только русские буквы, минимум 2 символа."
    )

    # Телефон: +7 900 000 00 00 или 89000000000
    phone_validator = RegexValidator(
        regex=r'^(\+7\s?\d{3}\s?\d{3}\s?\d{2}\s?\d{2}|8\d{10})$',
        message="Телефон должен быть в формате: +7 900 000 00 00 или 89000000000"
    )

    first_name = forms.CharField(
        min_length=2,
        max_length=100,
        label="Имя",
        validators=[name_validator],
        error_messages={
            'required': 'Имя обязательно',
            'min_length': 'Слишком короткое имя',
            'max_length': 'Слишком длинное имя',
        },
        widget=forms.TextInput(attrs={
            'placeholder': 'Иван',
            'pattern': '[А-ЯЁа-яё]{2,}',
            'title': 'Только русские буквы, минимум 2'
        })
    )

    last_name = forms.CharField(
        min_length=2,
        max_length=100,
        label="Фамилия",
        validators=[name_validator],
        error_messages={
            'required': 'Фамилия обязательна',
            'min_length': 'Слишком короткая фамилия',
            'max_length': 'Слишком длинная фамилия',
        },
        widget=forms.TextInput(attrs={
            'placeholder': 'Иванов',
            'pattern': '[А-ЯЁа-яё]{2,}',
            'title': 'Только русские буквы, минимум 2'
        })
    )

    email = forms.EmailField(
        label="Email",
        error_messages={
            'required': 'Email обязателен',
            'invalid': 'Введите корректный email (например: ivan@example.com)'
        },
        widget=forms.EmailInput(attrs={'placeholder': 'ivan@example.com'})
    )

    phone = forms.CharField(
        max_length=18,
        label="Телефон",
        validators=[phone_validator],
        error_messages={
            'required': 'Телефон обязателен',
            'max_length': 'Слишком длинный номер',
        },
        widget=forms.TextInput(attrs={
            'placeholder': '+7 900 000 00 00',
            'inputmode': 'numeric'
        })
    )

    def clean_first_name(self):
        value = self.cleaned_data['first_name'].strip()
        if not value:
            raise forms.ValidationError("Имя не может быть пустым")
        return value.capitalize()

    def clean_last_name(self):
        value = self.cleaned_data['last_name'].strip()
        if not value:
            raise forms.ValidationError("Фамилия не может быть пустой")
        return value.capitalize()

    def clean_phone(self):
        phone = self.cleaned_data['phone'].strip()
        phone = phone.replace(' ', '').replace('-', '')
        if phone.startswith('+7'):
            phone = '8' + phone[2:]
        return phone

class UploadFileForm(forms.Form):
    file = forms.FileField(
        label="Выберите XML-файл",
        widget=forms.FileInput(attrs={'accept': '.xml'})
    )