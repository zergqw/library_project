import shutil
import tempfile

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse

from .models import Author, Book, Genre


class BookCatalogSearchTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.temp_media_root = tempfile.mkdtemp()
        cls.override = override_settings(MEDIA_ROOT=cls.temp_media_root)
        cls.override.enable()

    @classmethod
    def tearDownClass(cls):
        cls.override.disable()
        shutil.rmtree(cls.temp_media_root, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.bulgakov = Author.objects.create(first_name='Михаил', last_name='Булгаков')
        self.pushkin = Author.objects.create(first_name='Александр', last_name='Пушкин')

        self.roman = Genre.objects.create(name='Роман')
        self.fantasy = Genre.objects.create(name='Фантастика')
        self.poetry = Genre.objects.create(name='Поэзия')

        self.master = Book.objects.create(
            title='Мастер и Маргарита',
            author=self.bulgakov,
            summary='Роман о добре и зле.',
            isbn='1111111111111',
            year=1967,
        )
        self.master.genre.add(self.roman, self.fantasy)

        self.dog = Book.objects.create(
            title='Собачье сердце',
            author=self.bulgakov,
            summary='Повесть о профессоре Преображенском.',
            isbn='2222222222222',
            year=1925,
        )
        self.dog.genre.add(self.fantasy)

        self.onegin = Book.objects.create(
            title='Евгений Онегин',
            author=self.pushkin,
            summary='Роман в стихах.',
            isbn='3333333333333',
            year=1833,
        )
        self.onegin.genre.add(self.roman, self.poetry)

    def test_index_shows_statistics_and_latest_books(self):
        response = self.client.get(reverse('catalog:index'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['num_books'], 3)
        self.assertEqual(response.context['num_authors'], 2)
        self.assertEqual(
            list(response.context['latest_books']),
            [self.onegin, self.dog, self.master],
        )
        self.assertContains(response, self.onegin.title)

    def test_book_list_without_search_returns_all_books(self):
        response = self.client.get(reverse('catalog:book_list'))

        self.assertEqual(response.status_code, 200)
        self.assertQuerySetEqual(
            response.context['books'].order_by('id'),
            Book.objects.order_by('id'),
            transform=lambda book: book,
        )
        self.assertEqual(response.context['search_query'], '')
        self.assertEqual(response.context['selected_author'], '')
        self.assertEqual(response.context['selected_genre'], '')

    def test_book_list_filters_by_title_query_case_insensitively(self):
        response = self.client.get(reverse('catalog:book_list'), {'q': 'маСТер'})

        self.assertEqual(response.status_code, 200)
        self.assertQuerySetEqual(
            response.context['books'],
            [self.master],
            transform=lambda book: book,
        )
        self.assertEqual(response.context['search_query'], 'маСТер')

    def test_book_list_filters_by_author(self):
        response = self.client.get(reverse('catalog:book_list'), {'author': str(self.pushkin.id)})

        self.assertEqual(response.status_code, 200)
        self.assertQuerySetEqual(
            response.context['books'],
            [self.onegin],
            transform=lambda book: book,
        )
        self.assertEqual(response.context['selected_author'], str(self.pushkin.id))

    def test_book_list_filters_by_genre(self):
        response = self.client.get(reverse('catalog:book_list'), {'genre': str(self.poetry.id)})

        self.assertEqual(response.status_code, 200)
        self.assertQuerySetEqual(
            response.context['books'],
            [self.onegin],
            transform=lambda book: book,
        )
        self.assertEqual(response.context['selected_genre'], str(self.poetry.id))

    def test_book_list_combines_search_author_and_genre_filters(self):
        response = self.client.get(
            reverse('catalog:book_list'),
            {
                'q': 'сердце',
                'author': str(self.bulgakov.id),
                'genre': str(self.fantasy.id),
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertQuerySetEqual(
            response.context['books'],
            [self.dog],
            transform=lambda book: book,
        )

    def test_book_list_with_unknown_query_returns_empty_result(self):
        response = self.client.get(reverse('catalog:book_list'), {'q': 'гарри поттер'})

        self.assertEqual(response.status_code, 200)
        self.assertQuerySetEqual(response.context['books'], [])

    def test_book_detail_shows_publication_year(self):
        response = self.client.get(reverse('catalog:book_detail', args=[self.master.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '1967')

    def test_book_detail_shows_cover_image_when_uploaded(self):
        uploaded_cover = SimpleUploadedFile(
            'cover.gif',
            (
                b'GIF89a\x01\x00\x01\x00\x80\x00\x00'
                b'\x00\x00\x00\xff\xff\xff!\xf9\x04\x01'
                b'\x00\x00\x00\x00,\x00\x00\x00\x00\x01'
                b'\x00\x01\x00\x00\x02\x02D\x01\x00;'
            ),
            content_type='image/gif',
        )
        self.master.cover = uploaded_cover
        self.master.save()

        response = self.client.get(reverse('catalog:book_detail', args=[self.master.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<img', html=False)
        self.assertContains(response, self.master.cover.url)
