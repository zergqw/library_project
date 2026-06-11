from datetime import date

from django.db import models

from apps.catalog.models import BookInstance
from apps.users.models import Reader


class Loan(models.Model):
    book_instance = models.ForeignKey(BookInstance, on_delete=models.CASCADE, verbose_name='Экземпляр книги')
    reader = models.ForeignKey(Reader, on_delete=models.CASCADE, verbose_name='Читатель')
    loan_date = models.DateField('Дата выдачи', auto_now_add=True)
    return_date = models.DateField('Дата возврата (план)', null=True, blank=True)
    actual_return_date = models.DateField('Дата возврата (факт)', null=True, blank=True)

    class Meta:
        verbose_name = 'Выдача'
        verbose_name_plural = 'Выдачи'
        constraints = [
            models.UniqueConstraint(
                fields=['book_instance'],
                condition=models.Q(actual_return_date__isnull=True),
                name='unique_active_loan_per_book_instance',
            ),
        ]

    @property
    def is_overdue(self):
        return (
            self.actual_return_date is None
            and self.return_date is not None
            and self.return_date < date.today()
        )

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        expected_status = 'a' if self.actual_return_date else 'o'
        if self.book_instance.status != expected_status:
            self.book_instance.status = expected_status
            self.book_instance.save(update_fields=['status'])

    def __str__(self):
        return f'{self.reader} взял {self.book_instance.book.title}'
