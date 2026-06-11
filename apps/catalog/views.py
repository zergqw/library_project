from django.shortcuts import get_object_or_404, render

from .models import Author, Book, BookInstance, Genre


def index(request):
    """Главная страница библиотеки."""
    context = {
        'num_books': Book.objects.count(),
        'num_instances': BookInstance.objects.count(),
        'num_available_instances': BookInstance.objects.filter(status='a').count(),
        'num_authors': Author.objects.count(),
        'latest_books': Book.objects.select_related('author').order_by('-id')[:3],
    }
    return render(request, 'catalog/index.html', context)


def book_list(request):
    search_query = request.GET.get('q', '').strip()
    selected_author = request.GET.get('author', '').strip()
    selected_genre = request.GET.get('genre', '').strip()

    books = Book.objects.select_related('author').prefetch_related('genre').all()

    if selected_author.isdigit():
        books = books.filter(author_id=int(selected_author))

    if selected_genre.isdigit():
        books = books.filter(genre__id=int(selected_genre))

    if search_query:
        normalized_query = search_query.casefold()
        matching_ids = [book.id for book in books if normalized_query in book.title.casefold()]
        books = books.filter(id__in=matching_ids)

    context = {
        'books': books.distinct(),
        'authors': Author.objects.order_by('last_name', 'first_name'),
        'genres': Genre.objects.order_by('name'),
        'search_query': search_query,
        'selected_author': selected_author,
        'selected_genre': selected_genre,
    }
    return render(request, 'catalog/book_list.html', context)


def book_detail(request, pk):
    """Страница книги и всех ее физических экземпляров."""
    book = get_object_or_404(Book.objects.select_related('author').prefetch_related('genre'), id=pk)
    instances = book.bookinstance_set.all()
    return render(request, 'catalog/book_detail.html', {'book': book, 'instances': instances})


def author_list(request):
    authors = Author.objects.all()
    return render(request, 'catalog/author_list.html', {'authors': authors})


def author_detail(request, pk):
    author = get_object_or_404(Author, id=pk)
    return render(request, 'catalog/author_detail.html', {'author': author})
