from django.db import models
from django.core.validators import RegexValidator

class Contact(models.Model):
    name_validator = RegexValidator(
        regex=r'^[А-ЯЁа-яё]{2,}$',
        message="Только русские буквы, минимум 2 символа."
    )
    phone_validator = RegexValidator(
        regex=r'^(\+7\s?\d{3}\s?\d{3}\s?\d{2}\s?\d{2}|8\d{10})$',
        message="Формат: +7 900 000 00 00 или 89000000000"
    )

    first_name = models.CharField(max_length=100, validators=[name_validator])
    last_name = models.CharField(max_length=100, validators=[name_validator])
    email = models.EmailField()
    phone = models.CharField(max_length=18, validators=[phone_validator])

    class Meta:
        unique_together = ['first_name', 'last_name', 'email', 'phone']  # Дубликат по всем полям

    def __str__(self):
        return f"{self.first_name} {self.last_name}"