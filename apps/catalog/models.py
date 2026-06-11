from django.db import models


class Genre(models.Model):
    name = models.CharField('Жанр', max_length=100)

    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'

    def __str__(self):
        return self.name


class Author(models.Model):
    first_name = models.CharField('Имя', max_length=100)
    last_name = models.CharField('Фамилия', max_length=100)
    date_of_birth = models.DateField('Дата рождения', null=True, blank=True)

    class Meta:
        verbose_name = 'Автор'
        verbose_name_plural = 'Авторы'

    def __str__(self):
        return f'{self.last_name}, {self.first_name}'


class Book(models.Model):
    title = models.CharField('Название', max_length=200)
    author = models.ForeignKey(Author, on_delete=models.SET_NULL, null=True, verbose_name='Автор')
    summary = models.TextField('Аннотация', max_length=1000)
    isbn = models.CharField('ISBN', max_length=13, unique=True)
    year = models.PositiveSmallIntegerField('Год издания', null=True, blank=True)
    cover = models.ImageField('Обложка', upload_to='books/covers/', null=True, blank=True)
    genre = models.ManyToManyField(Genre, verbose_name='Жанр')

    class Meta:
        verbose_name = 'Книга'
        verbose_name_plural = 'Книги'

    def __str__(self):
        return self.title


class BookInstance(models.Model):
    """Конкретный физический экземпляр книги."""

    book = models.ForeignKey(Book, on_delete=models.CASCADE, verbose_name='Книга')
    inv_number = models.CharField('Инвентарный номер', max_length=20, unique=True)

    LOAN_STATUS = (
        ('m', 'На обслуживании'),
        ('o', 'Выдана'),
        ('a', 'Доступна'),
        ('r', 'Зарезервирована'),
    )

    status = models.CharField(max_length=1, choices=LOAN_STATUS, default='a', verbose_name='Статус')

    class Meta:
        verbose_name = 'Экземпляр книги'
        verbose_name_plural = 'Экземпляры книг'

    def __str__(self):
        return f'{self.inv_number} ({self.book.title})'
