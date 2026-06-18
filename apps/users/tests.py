from datetime import date, timedelta
from io import StringIO
from unittest.mock import patch

from django.contrib.auth.models import User
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse

from apps.catalog.models import Author, Book, BookInstance, Genre
from apps.loans.models import Loan

from .models import Reader


class ReaderRegistrationTests(TestCase):
    def test_signup_creates_user_and_reader_profile(self):
        response = self.client.post(
            reverse('users:sign_up'),
            {
                'username': 'new_reader',
                'first_name': 'Иван',
                'last_name': 'Петров',
                'email': 'reader@example.com',
                'password1': 'StrongPass123',
                'password2': 'StrongPass123',
                'ticket_number': 'T-100',
                'phone': '+79992223344',
            },
        )

        user = User.objects.get(username='new_reader')
        reader = Reader.objects.get(user=user)

        self.assertRedirects(response, reverse('login'))
        self.assertEqual(user.first_name, 'Иван')
        self.assertEqual(user.last_name, 'Петров')
        self.assertEqual(user.email, 'reader@example.com')
        self.assertEqual(reader.ticket_number, 'T-100')
        self.assertEqual(reader.phone, '+79992223344')

    def test_signup_does_not_create_reader_when_form_is_invalid(self):
        response = self.client.post(
            reverse('users:sign_up'),
            {
                'username': 'new_reader',
                'password1': 'StrongPass123',
                'password2': 'DifferentPass123',
                'ticket_number': 'T-100',
                'phone': '+79992223344',
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username='new_reader').exists())
        self.assertFalse(Reader.objects.exists())


class EnsureSuperuserCommandTests(TestCase):
    def test_command_skips_creation_without_password(self):
        out = StringIO()

        with patch.dict('os.environ', {}, clear=True):
            call_command('ensure_superuser', stdout=out)

        self.assertFalse(User.objects.filter(username='admin').exists())
        self.assertIn('Superuser creation skipped', out.getvalue())

    def test_command_creates_superuser_from_environment(self):
        out = StringIO()

        with patch.dict(
            'os.environ',
            {
                'DJANGO_SUPERUSER_USERNAME': 'render-admin',
                'DJANGO_SUPERUSER_EMAIL': 'render-admin@example.com',
                'DJANGO_SUPERUSER_PASSWORD': 'StrongRenderPass123',
            },
            clear=True,
        ):
            call_command('ensure_superuser', stdout=out)

        user = User.objects.get(username='render-admin')
        self.assertEqual(user.email, 'render-admin@example.com')
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.check_password('StrongRenderPass123'))
        self.assertIn('Superuser "render-admin" created', out.getvalue())


class ProfileViewTests(TestCase):
    def setUp(self):
        self.author = Author.objects.create(first_name='Александр', last_name='Пушкин')
        self.genre = Genre.objects.create(name='Поэзия')
        self.book = Book.objects.create(
            title='Евгений Онегин',
            author=self.author,
            summary='Роман в стихах',
            isbn='9876543210123',
            year=1833,
        )
        self.book.genre.add(self.genre)

        self.reader_user = User.objects.create_user(username='reader', password='pass12345')
        self.reader = Reader.objects.create(
            user=self.reader_user,
            ticket_number='T-002',
            phone='+79991111111',
        )

    def test_profile_url_is_available_without_double_prefix(self):
        self.client.login(username='reader', password='pass12345')

        response = self.client.get(reverse('users:profile'))

        self.assertEqual(reverse('users:profile'), '/profile/')
        self.assertEqual(response.status_code, 200)

    def test_profile_splits_active_loans_and_history(self):
        active_instance = BookInstance.objects.create(
            book=self.book,
            inv_number='INV-101',
            status='o',
        )
        returned_instance = BookInstance.objects.create(
            book=self.book,
            inv_number='INV-102',
            status='a',
        )

        active_loan = Loan.objects.create(
            book_instance=active_instance,
            reader=self.reader,
            return_date=date.today() + timedelta(days=14),
        )
        returned_loan = Loan.objects.create(
            book_instance=returned_instance,
            reader=self.reader,
            return_date=date.today(),
            actual_return_date=date.today(),
        )

        self.client.login(username='reader', password='pass12345')
        response = self.client.get(reverse('users:profile'))

        self.assertEqual(list(response.context['active_loans']), [active_loan])
        self.assertEqual(list(response.context['loan_history']), [returned_loan])

    def test_profile_marks_overdue_loans(self):
        overdue_instance = BookInstance.objects.create(
            book=self.book,
            inv_number='INV-103',
            status='o',
        )
        overdue_loan = Loan.objects.create(
            book_instance=overdue_instance,
            reader=self.reader,
            return_date=date.today() - timedelta(days=3),
        )

        self.client.login(username='reader', password='pass12345')
        response = self.client.get(reverse('users:profile'))

        self.assertEqual(list(response.context['active_loans']), [overdue_loan])
        self.assertContains(response, 'Просрочена')

    def test_staff_profile_redirects_to_admin_without_reader_profile(self):
        staff_user = User.objects.create_user(
            username='admin',
            password='pass12345',
            is_staff=True,
        )
        self.client.force_login(staff_user)

        response = self.client.get(reverse('users:profile'))

        self.assertRedirects(response, reverse('admin:index'))
