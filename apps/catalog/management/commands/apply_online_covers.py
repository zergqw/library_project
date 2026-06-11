import json
import time
from io import BytesIO
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from PIL import Image, ImageDraw, ImageEnhance, ImageFont, UnidentifiedImageError

from apps.catalog.models import Book


COVER_SOURCES = {
    '1111111111111': {
        'label': 'Портрет Михаила Булгакова',
        'url': 'https://commons.wikimedia.org/wiki/Special:FilePath/%D0%9C%D0%B8%D1%85%D0%B0%D0%B8%D0%BB-%D0%91%D1%83%D0%BB%D0%B3%D0%B0%D0%BA%D0%BE%D0%B2.jpg?width=900',
        'source_page': 'https://en.wikipedia.org/wiki/Mikhail_Bulgakov',
        'overlay': True,
    },
    '1234567890123': {
        'label': 'War and Peace cover from Project Gutenberg',
        'url': 'https://www.gutenberg.org/cache/epub/2600/images/cover.jpg',
        'source_page': 'https://www.gutenberg.org/cache/epub/2600/pg2600-images.html',
        'overlay': False,
    },
    '3333333333333': {
        'label': 'Eugene Onegin illustration by E. Samokish-Sudkovskaya',
        'url': 'https://commons.wikimedia.org/wiki/Special:FilePath/Eugene_Onegin_(Samokish-Sudkovskaya)_11.jpg?width=900',
        'source_page': 'https://commons.wikimedia.org/wiki/File:Eugene_Onegin_(Samokish-Sudkovskaya)_11.jpg',
        'overlay': True,
    },
    '9785000000011': {
        'label': 'Wax-sealed letters',
        'url': 'https://commons.wikimedia.org/wiki/Special:FilePath/Sealing_wax_on_letters.jpg?width=900',
        'source_page': 'https://commons.wikimedia.org/wiki/File:Sealing_wax_on_letters.jpg',
        'overlay': True,
    },
    '9785000000028': {
        'label': 'Old books',
        'url': 'https://commons.wikimedia.org/wiki/Special:FilePath/Old_Books_01.JPG?width=900',
        'source_page': 'https://commons.wikimedia.org/wiki/File:Old_Books_01.JPG',
        'overlay': True,
    },
    '9785000000035': {
        'label': 'Palace Bridge during White Nights',
        'url': 'https://upload.wikimedia.org/wikipedia/commons/thumb/e/e6/NevaBridgeWhiteNight.JPG/500px-NevaBridgeWhiteNight.JPG',
        'source_page': 'https://en.wikipedia.org/wiki/Climate_of_Saint_Petersburg',
        'overlay': True,
    },
    '9785000000042': {
        'label': 'Laptop with program code',
        'url': 'https://commons.wikimedia.org/wiki/Special:FilePath/Laptop_Programmcode.jpg?width=900',
        'source_page': 'https://commons.wikimedia.org/wiki/File:Laptop_Programmcode.jpg',
        'overlay': True,
    },
    '9785000000059': {
        'label': 'Artificial neural network diagram',
        'url': 'https://commons.wikimedia.org/wiki/Special:FilePath/Artificial_neural_network_image_recognition.png?width=900',
        'source_page': 'https://commons.wikimedia.org/wiki/File:Artificial_neural_network_image_recognition.png',
        'overlay': True,
    },
    '9785000000066': {
        'label': 'Astronomical clock gears',
        'url': 'https://commons.wikimedia.org/wiki/Special:FilePath/Gears_-_Astronomical_clock_in_Copenhagen_City_Hall_-_Denmark.jpg?width=900',
        'source_page': 'https://commons.wikimedia.org/wiki/File:Gears_-_Astronomical_clock_in_Copenhagen_City_Hall_-_Denmark.jpg',
        'overlay': True,
    },
    '9785000000073': {
        'label': 'HMS Terror in the Arctic Regions',
        'url': 'https://commons.wikimedia.org/wiki/Special:FilePath/William_Smyth_HMS_Terror_in_the_Arctic_Regions_Summer_1837.jpg?width=900',
        'source_page': 'https://commons.wikimedia.org/wiki/File:William_Smyth_HMS_Terror_in_the_Arctic_Regions_Summer_1837.jpg',
        'overlay': True,
    },
    '9785000000080': {
        'label': 'Coding workstation',
        'url': 'https://commons.wikimedia.org/wiki/Special:FilePath/Coding_workstation_(Unsplash).jpg?width=900',
        'source_page': 'https://commons.wikimedia.org/wiki/File:Coding_workstation_(Unsplash).jpg',
        'overlay': True,
    },
    '9785000000097': {
        'label': 'Garden through an open window',
        'url': 'https://commons.wikimedia.org/wiki/Special:FilePath/View_into_a_garden_through_an_open_ground_floor_window_in_Germany.jpg?width=900',
        'source_page': 'https://commons.wikimedia.org/wiki/File:View_into_a_garden_through_an_open_ground_floor_window_in_Germany.jpg',
        'overlay': True,
    },
    '9785000000103': {
        'label': 'Quiet library reading room',
        'url': 'https://commons.wikimedia.org/wiki/Special:FilePath/Bibliothek_Lesesaal_ruhig.jpg?width=900',
        'source_page': 'https://commons.wikimedia.org/wiki/File:Bibliothek_Lesesaal_ruhig.jpg',
        'overlay': True,
    },
    '9785000000110': {
        'label': 'Baroque library in Prague',
        'url': 'https://commons.wikimedia.org/wiki/Special:FilePath/A_Baroque_library,_Prague_-_7529.jpg?width=900',
        'source_page': 'https://commons.wikimedia.org/wiki/File:A_Baroque_library,_Prague_-_7529.jpg',
        'overlay': True,
    },
    '9785000000127': {
        'label': 'Cross-written letter',
        'url': 'https://commons.wikimedia.org/wiki/Special:FilePath/Crossed_letter.jpg?width=900',
        'source_page': 'https://commons.wikimedia.org/wiki/File:Crossed_letter.jpg',
        'overlay': True,
    },
}


class Command(BaseCommand):
    help = 'Downloads open web images and applies them as book covers.'

    def handle(self, *args, **options):
        output_dir = Path(settings.MEDIA_ROOT) / 'books' / 'covers' / 'online'
        output_dir.mkdir(parents=True, exist_ok=True)

        applied = []
        missing = []

        for isbn, source in COVER_SOURCES.items():
            try:
                book = Book.objects.get(isbn=isbn)
            except Book.DoesNotExist:
                missing.append(isbn)
                continue

            filename = f'{isbn}.jpg'
            output_path = output_dir / filename
            if not output_path.exists():
                try:
                    image = self.download_image(source['url'])
                except (OSError, URLError, UnidentifiedImageError) as exc:
                    raise CommandError(f'Could not download cover for {isbn}: {exc}') from exc

                cover = self.make_cover(image, book, source['overlay'])
                cover.save(output_path, format='JPEG', quality=90, optimize=True)
                time.sleep(1.25)

            book.cover = f'books/covers/online/{filename}'
            book.save(update_fields=['cover'])
            applied.append((book.title, isbn, source['label']))

        sources_path = output_dir / 'sources.json'
        sources_path.write_text(
            json.dumps(COVER_SOURCES, ensure_ascii=False, indent=2),
            encoding='utf-8',
        )

        for title, isbn, label in applied:
            self.stdout.write(f'Applied: {isbn} - {title} ({label})')

        if missing:
            self.stdout.write(self.style.WARNING(f'Skipped missing ISBNs: {", ".join(missing)}'))

        self.stdout.write(self.style.SUCCESS(f'Applied {len(applied)} online covers.'))
        self.stdout.write(f'Source metadata: {sources_path}')

    def download_image(self, url):
        request = Request(url, headers={'User-Agent': 'library-project-demo-seeder/1.0'})
        last_error = None
        for attempt in range(4):
            try:
                with urlopen(request, timeout=30) as response:
                    data = response.read()
                return Image.open(BytesIO(data)).convert('RGB')
            except HTTPError as exc:
                last_error = exc
                if exc.code != 429:
                    raise
                time.sleep(3 + attempt * 3)
        raise last_error

    def make_cover(self, image, book, overlay):
        width, height = 900, 1300
        image = self.crop_to_cover(image, width, height)

        if overlay:
            image = ImageEnhance.Color(image).enhance(0.88)
            image = ImageEnhance.Contrast(image).enhance(0.92)
            draw = ImageDraw.Draw(image, 'RGBA')
            draw.rectangle((0, 0, width, height), fill=(0, 0, 0, 54))
            draw.rectangle((60, 72, width - 60, height - 72), outline=(255, 255, 255, 190), width=6)
            draw.rectangle((0, height - 455, width, height), fill=(0, 0, 0, 170))

            title_font = self.get_font(58)
            author_font = self.get_font(34)
            meta_font = self.get_font(26)

            y = height - 390
            for line in self.wrap_text(book.title.upper(), title_font, width - 150, draw):
                bbox = draw.textbbox((0, 0), line, font=title_font)
                draw.text(((width - (bbox[2] - bbox[0])) / 2, y), line, font=title_font, fill=(255, 255, 255, 255))
                y += 70

            author_name = str(book.author).replace(',', '') if book.author else ''
            bbox = draw.textbbox((0, 0), author_name, font=author_font)
            draw.text(((width - (bbox[2] - bbox[0])) / 2, height - 148), author_name, font=author_font, fill=(235, 235, 235, 255))

            if book.year:
                year = str(book.year)
                bbox = draw.textbbox((0, 0), year, font=meta_font)
                draw.text(((width - (bbox[2] - bbox[0])) / 2, height - 98), year, font=meta_font, fill=(220, 220, 220, 255))

        return image

    def crop_to_cover(self, image, width, height):
        target_ratio = width / height
        source_ratio = image.width / image.height

        if source_ratio > target_ratio:
            new_width = int(image.height * target_ratio)
            left = (image.width - new_width) // 2
            image = image.crop((left, 0, left + new_width, image.height))
        else:
            new_height = int(image.width / target_ratio)
            top = (image.height - new_height) // 2
            image = image.crop((0, top, image.width, top + new_height))

        return image.resize((width, height), Image.Resampling.LANCZOS)

    def get_font(self, size):
        for path in [
            Path('C:/Windows/Fonts/arial.ttf'),
            Path('C:/Windows/Fonts/segoeui.ttf'),
            Path('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'),
        ]:
            if path.exists():
                return ImageFont.truetype(str(path), size)
        return ImageFont.load_default()

    def wrap_text(self, text, font, max_width, draw):
        words = text.split()
        lines = []
        current = ''

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

        return lines[:4]
