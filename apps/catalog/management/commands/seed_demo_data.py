from datetime import date, timedelta
from pathlib import Path
import random
import textwrap

from django.conf import settings
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.db import transaction
from PIL import Image, ImageDraw, ImageFont

from apps.catalog.models import Author, Book, BookInstance, Genre
from apps.loans.models import Loan
from apps.users.models import Reader


PASSWORD = 'demo12345'


GENRES = [
    'Программирование',
    'Научная фантастика',
    'Детектив',
    'История',
    'Психология',
    'Бизнес',
    'Фэнтези',
    'Учебная литература',
    'Классика',
    'Современная проза',
]


AUTHORS = [
    ('Анна', 'Воронцова', date(1981, 4, 17)),
    ('Илья', 'Соколов', date(1977, 9, 2)),
    ('Мария', 'Лебедева', date(1990, 1, 21)),
    ('Сергей', 'Орлов', date(1984, 11, 6)),
    ('Виктория', 'Морозова', date(1988, 7, 14)),
    ('Павел', 'Громов', date(1972, 3, 30)),
    ('Елена', 'Романова', date(1969, 12, 9)),
    ('Кирилл', 'Волков', date(1992, 5, 23)),
    ('Наталья', 'Крылова', date(1986, 8, 11)),
    ('Дмитрий', 'Белов', date(1979, 10, 4)),
    ('Ольга', 'Миронова', date(1991, 2, 18)),
    ('Алексей', 'Руднев', date(1983, 6, 25)),
]


BOOKS = [
    {
        'title': 'Тени старого архива',
        'author': 'Воронцова',
        'isbn': '9785000000011',
        'year': 2019,
        'genres': ['Детектив', 'Современная проза'],
        'summary': 'Библиотекарь находит в закрытом фонде письма, которые меняют историю старого города.',
        'palette': ('#263238', '#f2c14e', '#d95d39'),
    },
    {
        'title': 'Кодекс библиотекаря',
        'author': 'Соколов',
        'isbn': '9785000000028',
        'year': 2021,
        'genres': ['Детектив', 'История'],
        'summary': 'Расследование кражи редкого издания превращается в экскурсию по тайным правилам книжного мира.',
        'palette': ('#1f3a5f', '#f7e7ce', '#b85042'),
    },
    {
        'title': 'Звезды над Невой',
        'author': 'Лебедева',
        'isbn': '9785000000035',
        'year': 2018,
        'genres': ['Научная фантастика', 'Современная проза'],
        'summary': 'Молодая астрофизик возвращается в Петербург и обнаруживает сигнал из будущего.',
        'palette': ('#182747', '#79a7d3', '#f6d365'),
    },
    {
        'title': 'Практическая Django-библиотека',
        'author': 'Орлов',
        'isbn': '9785000000042',
        'year': 2024,
        'genres': ['Программирование', 'Учебная литература'],
        'summary': 'Пошаговое руководство по созданию веб-приложений для учета книг, читателей и выдач.',
        'palette': ('#0f766e', '#ffffff', '#f59e0b'),
    },
    {
        'title': 'Машинное обучение без паники',
        'author': 'Морозова',
        'isbn': '9785000000059',
        'year': 2023,
        'genres': ['Программирование', 'Учебная литература'],
        'summary': 'Понятное введение в модели, датасеты и оценку качества без лишней математики.',
        'palette': ('#312e81', '#c4b5fd', '#22c55e'),
    },
    {
        'title': 'Город медных часов',
        'author': 'Громов',
        'isbn': '9785000000066',
        'year': 2017,
        'genres': ['Фэнтези', 'Научная фантастика'],
        'summary': 'В городе, где время продают на рынках, ученик часовщика ищет пропавшую минуту.',
        'palette': ('#3d2c29', '#c47f2f', '#f4e1b8'),
    },
    {
        'title': 'История одной экспедиции',
        'author': 'Романова',
        'isbn': '9785000000073',
        'year': 2015,
        'genres': ['История', 'Классика'],
        'summary': 'Документальная проза о северной экспедиции, дневниках и выборе, который меняет судьбы.',
        'palette': ('#0f172a', '#e2e8f0', '#38bdf8'),
    },
    {
        'title': 'Алгоритмы каждый день',
        'author': 'Волков',
        'isbn': '9785000000080',
        'year': 2022,
        'genres': ['Программирование', 'Учебная литература'],
        'summary': 'Практические задачи, структуры данных и приемы анализа для начинающих разработчиков.',
        'palette': ('#111827', '#60a5fa', '#f97316'),
    },
    {
        'title': 'Сад за стеклянной дверью',
        'author': 'Крылова',
        'isbn': '9785000000097',
        'year': 2020,
        'genres': ['Современная проза', 'Психология'],
        'summary': 'Тихий роман о памяти, семейных письмах и доме, который помогает начать сначала.',
        'palette': ('#14532d', '#bbf7d0', '#f9a8d4'),
    },
    {
        'title': 'Архитектура тишины',
        'author': 'Белов',
        'isbn': '9785000000103',
        'year': 2016,
        'genres': ['Психология', 'Бизнес'],
        'summary': 'Книга о внимании, рабочих ритуалах и проектировании среды для глубокого мышления.',
        'palette': ('#334155', '#f8fafc', '#14b8a6'),
    },
    {
        'title': 'Полка номер семь',
        'author': 'Миронова',
        'isbn': '9785000000110',
        'year': 2025,
        'genres': ['Детектив', 'Современная проза'],
        'summary': 'В обычной районной библиотеке исчезают только книги с одной полки, и у каждой потери есть адресат.',
        'palette': ('#7c2d12', '#fed7aa', '#2563eb'),
    },
    {
        'title': 'Короткие письма в июне',
        'author': 'Руднев',
        'isbn': '9785000000127',
        'year': 2020,
        'genres': ['Классика', 'Современная проза'],
        'summary': 'Сборник рассказов о летних поездках, случайных встречах и письмах, которые не успели отправить.',
        'palette': ('#365314', '#fef3c7', '#fb7185'),
    },
]


READERS = [
    ('demo.reader1', 'Ирина', 'Кузнецова', 'LIB-2026-001', '+7 900 111-22-33'),
    ('demo.reader2', 'Максим', 'Федоров', 'LIB-2026-002', '+7 900 222-33-44'),
    ('demo.reader3', 'Алина', 'Павлова', 'LIB-2026-003', '+7 900 333-44-55'),
    ('demo.reader4', 'Никита', 'Смирнов', 'LIB-2026-004', '+7 900 444-55-66'),
    ('demo.reader5', 'Екатерина', 'Николаева', 'LIB-2026-005', '+7 900 555-66-77'),
    ('demo.reader6', 'Даниил', 'Иванов', 'LIB-2026-006', '+7 900 666-77-88'),
]


class Command(BaseCommand):
    help = 'Creates demo genres, authors, books, covers, readers, and loans.'

    def handle(self, *args, **options):
        random.seed(42)

        with transaction.atomic():
            genres = self.create_genres()
            authors = self.create_authors()
            books = self.create_books(authors, genres)
            instances = self.create_instances(books)
            readers = self.create_readers()
            loans = self.create_loans(instances, readers)

        self.stdout.write(self.style.SUCCESS('Demo data is ready.'))
        self.stdout.write(
            f'Genres: {len(genres)}, authors: {len(authors)}, books: {len(books)}, '
            f'instances: {len(instances)}, readers: {len(readers)}, loans touched: {len(loans)}.'
        )
        self.stdout.write(f'Demo users password: {PASSWORD}')

    def create_genres(self):
        return {name: Genre.objects.get_or_create(name=name)[0] for name in GENRES}

    def create_authors(self):
        authors = {}
        for first_name, last_name, date_of_birth in AUTHORS:
            author, _ = Author.objects.update_or_create(
                first_name=first_name,
                last_name=last_name,
                defaults={'date_of_birth': date_of_birth},
            )
            authors[last_name] = author
        return authors

    def create_books(self, authors, genres):
        books = []
        for item in BOOKS:
            cover_name = self.create_cover(item)
            book, _ = Book.objects.update_or_create(
                isbn=item['isbn'],
                defaults={
                    'title': item['title'],
                    'author': authors[item['author']],
                    'summary': item['summary'],
                    'year': item['year'],
                    'cover': cover_name,
                },
            )
            book.genre.set(genres[name] for name in item['genres'])
            books.append(book)
        return books

    def create_instances(self, books):
        instances = []
        for book_index, book in enumerate(books, start=1):
            for copy_index in range(1, 4):
                inv_number = f'DEMO-{book_index:03d}-{copy_index:02d}'
                instance, _ = BookInstance.objects.get_or_create(
                    inv_number=inv_number,
                    defaults={'book': book, 'status': 'a'},
                )
                if instance.book_id != book.id:
                    instance.book = book
                    instance.save(update_fields=['book'])
                instances.append(instance)
        return instances

    def create_readers(self):
        readers = []
        for username, first_name, last_name, ticket_number, phone in READERS:
            user, _ = User.objects.update_or_create(
                username=username,
                defaults={
                    'first_name': first_name,
                    'last_name': last_name,
                    'email': f'{username}@example.com',
                    'is_active': True,
                },
            )
            user.set_password(PASSWORD)
            user.save(update_fields=['password'])

            reader, _ = Reader.objects.update_or_create(
                ticket_number=ticket_number,
                defaults={'user': user, 'phone': phone},
            )
            readers.append(reader)

        librarian, _ = User.objects.update_or_create(
            username='demo.librarian',
            defaults={
                'first_name': 'Олег',
                'last_name': 'Библиотекарь',
                'email': 'demo.librarian@example.com',
                'is_staff': True,
                'is_active': True,
            },
        )
        librarian.set_password(PASSWORD)
        librarian.save(update_fields=['password'])

        return readers

    def create_loans(self, instances, readers):
        loans = []
        today = date.today()

        scenarios = [
            (0, 0, today - timedelta(days=5), today + timedelta(days=9), None),
            (4, 1, today - timedelta(days=21), today - timedelta(days=7), None),
            (8, 2, today - timedelta(days=35), today - timedelta(days=14), today - timedelta(days=12)),
            (12, 3, today - timedelta(days=3), today + timedelta(days=11), None),
            (16, 4, today - timedelta(days=42), today - timedelta(days=20), today - timedelta(days=18)),
            (20, 5, today - timedelta(days=18), today - timedelta(days=2), None),
            (24, 0, today - timedelta(days=60), today - timedelta(days=46), today - timedelta(days=40)),
            (28, 1, today - timedelta(days=7), today + timedelta(days=7), None),
        ]

        for instance_index, reader_index, loan_date, return_date, actual_return_date in scenarios:
            instance = instances[instance_index]
            reader = readers[reader_index]

            Loan.objects.filter(book_instance=instance).exclude(
                actual_return_date__isnull=False
            ).delete()

            loan, _ = Loan.objects.update_or_create(
                book_instance=instance,
                reader=reader,
                actual_return_date=actual_return_date,
                defaults={'return_date': return_date},
            )
            if loan.loan_date != loan_date:
                Loan.objects.filter(pk=loan.pk).update(loan_date=loan_date)
                loan.loan_date = loan_date
            loan.save()
            loans.append(loan)

        for instance in instances:
            has_active_loan = Loan.objects.filter(
                book_instance=instance,
                actual_return_date__isnull=True,
            ).exists()
            expected_status = 'o' if has_active_loan else 'a'
            if instance.status != expected_status:
                instance.status = expected_status
                instance.save(update_fields=['status'])

        return loans

    def create_cover(self, item):
        output_dir = Path(settings.MEDIA_ROOT) / 'books' / 'covers'
        output_dir.mkdir(parents=True, exist_ok=True)

        filename = f"{item['isbn']}.jpg"
        output_path = output_dir / filename

        width, height = 900, 1300
        background, primary, accent = item['palette']
        image = Image.new('RGB', (width, height), background)
        draw = ImageDraw.Draw(image)

        for i in range(18):
            x0 = -160 + i * 72
            draw.rectangle((x0, 0, x0 + 28, height), fill=primary)

        for i in range(9):
            radius = 140 + i * 32
            draw.ellipse(
                (width - radius - 80, 120 + i * 45, width + radius // 2, 120 + radius + i * 45),
                outline=accent,
                width=7,
            )

        draw.rectangle((86, 92, width - 86, height - 92), outline=primary, width=10)
        draw.rectangle((118, 124, width - 118, height - 124), outline=accent, width=4)

        title_font = self.get_font(70)
        author_font = self.get_font(42)
        meta_font = self.get_font(30)

        title_lines = self.wrap_text(item['title'].upper(), title_font, width - 260)
        y = 385
        for line in title_lines:
            bbox = draw.textbbox((0, 0), line, font=title_font)
            draw.text(((width - (bbox[2] - bbox[0])) / 2, y), line, font=title_font, fill='#ffffff')
            y += 82

        author = next(author for author in AUTHORS if author[1] == item['author'])
        author_text = f'{author[0]} {author[1]}'
        bbox = draw.textbbox((0, 0), author_text, font=author_font)
        draw.text(((width - (bbox[2] - bbox[0])) / 2, 235), author_text, font=author_font, fill=primary)

        year_text = str(item['year'])
        bbox = draw.textbbox((0, 0), year_text, font=meta_font)
        draw.text(((width - (bbox[2] - bbox[0])) / 2, height - 190), year_text, font=meta_font, fill=primary)

        image.save(output_path, quality=92)
        return f'books/covers/{filename}'

    def get_font(self, size):
        font_candidates = [
            Path('C:/Windows/Fonts/arial.ttf'),
            Path('C:/Windows/Fonts/segoeui.ttf'),
            Path('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'),
        ]
        for font_path in font_candidates:
            if font_path.exists():
                return ImageFont.truetype(str(font_path), size)
        return ImageFont.load_default()

    def wrap_text(self, text, font, max_width):
        words = text.split()
        lines = []
        current = ''

        probe = Image.new('RGB', (1, 1))
        draw = ImageDraw.Draw(probe)

        for word in words:
            candidate = f'{current} {word}'.strip()
            bbox = draw.textbbox((0, 0), candidate, font=font)
            if bbox[2] - bbox[0] <= max_width:
                current = candidate
                continue
            if current:
                lines.append(current)
            current = word

        if current:
            lines.append(current)

        if not lines:
            return textwrap.wrap(text, width=12)
        return lines
