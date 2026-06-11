from django.contrib.auth.models import User
from django.db import models


class Reader(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    ticket_number = models.CharField('Номер билета', max_length=20, unique=True)
    phone = models.CharField('Телефон', max_length=20)

    class Meta:
        verbose_name = 'Читатель'
        verbose_name_plural = 'Читатели'

    def __str__(self):
        return f'{self.user.last_name} ({self.ticket_number})'
