from django.contrib import admin

from .models import Author, Book, BookInstance, Genre

admin.site.register(Genre)


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('last_name', 'first_name', 'date_of_birth')


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'year', 'isbn')
    list_filter = ('genre', 'author', 'year')


@admin.register(BookInstance)
class BookInstanceAdmin(admin.ModelAdmin):
    list_display = ('book', 'status', 'inv_number', 'id')
    list_filter = ('status',)
    fieldsets = (
        (None, {'fields': ('book', 'inv_number')}),
        ('Статус доступности', {'fields': ('status',)}),
    )
