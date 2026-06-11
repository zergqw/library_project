from datetime import date, timedelta

from django.contrib.auth.models import User
from django.db import IntegrityError, transaction
from django.test import TestCase
from django.urls import reverse

from apps.catalog.models import Author, Book, BookInstance, Genre
from apps.users.models import Reader

from .models import Loan


class LoanViewsTests(TestCase):
    def setUp(self):
        self.author = Author.objects.create(first_name='Лев', last_name='Толстой')
        self.genre = Genre.objects.create(name='Роман')
        self.book = Book.objects.create(
            title='Война и мир',
            author=self.author,
            summary='Роман-эпопея',
            isbn='1234567890123',
            year=1869,
        )
        self.book.genre.add(self.genre)
        self.book_instance = BookInstance.objects.create(
            book=self.book,
            inv_number='INV-001',
            status='a',
        )

        self.reader_user = User.objects.create_user(username='reader', password='pass12345')
        self.reader = Reader.objects.create(
            user=self.reader_user,
            ticket_number='T-001',
            phone='+79990000000',
        )

        self.staff_user = User.objects.create_user(
            username='librarian',
            password='pass12345',
            is_staff=True,
        )

    def test_reader_can_take_available_book_instance(self):
        self.client.login(username='reader', password='pass12345')

        response = self.client.post(reverse('loans:borrow_book', args=[self.book_instance.pk]))

        self.book_instance.refresh_from_db()
        loan = Loan.objects.get(book_instance=self.book_instance)

        self.assertRedirects(response, reverse('catalog:book_detail', args=[self.book.pk]))
        self.assertEqual(self.book_instance.status, 'o')
        self.assertEqual(loan.reader, self.reader)
        self.assertEqual(loan.return_date, date.today() + timedelta(days=14))

    def test_anonymous_user_is_redirected_to_login_when_borrowing(self):
        borrow_url = reverse('loans:borrow_book', args=[self.book_instance.pk])

        response = self.client.post(borrow_url)

        self.assertRedirects(response, f'{reverse("login")}?next={borrow_url}')
        self.assertFalse(Loan.objects.exists())

    def test_reader_cannot_take_unavailable_book_instance(self):
        self.book_instance.status = 'o'
        self.book_instance.save(update_fields=['status'])
        self.client.login(username='reader', password='pass12345')

        response = self.client.post(reverse('loans:borrow_book', args=[self.book_instance.pk]))

        self.book_instance.refresh_from_db()

        self.assertRedirects(response, reverse('catalog:book_detail', args=[self.book.pk]))
        self.assertEqual(self.book_instance.status, 'o')
        self.assertFalse(Loan.objects.exists())

    def test_creating_active_loan_marks_book_instance_as_on_loan(self):
        Loan.objects.create(
            book_instance=self.book_instance,
            reader=self.reader,
            return_date=date.today() + timedelta(days=14),
        )

        self.book_instance.refresh_from_db()

        self.assertEqual(self.book_instance.status, 'o')

    def test_book_instance_cannot_have_two_active_loans(self):
        Loan.objects.create(
            book_instance=self.book_instance,
            reader=self.reader,
            return_date=date.today() + timedelta(days=14),
        )

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Loan.objects.create(
                    book_instance=self.book_instance,
                    reader=self.reader,
                    return_date=date.today() + timedelta(days=7),
                )

    def test_setting_actual_return_date_marks_book_instance_as_available(self):
        loan = Loan.objects.create(
            book_instance=self.book_instance,
            reader=self.reader,
            return_date=date.today() + timedelta(days=14),
        )

        loan.actual_return_date = date.today()
        loan.save(update_fields=['actual_return_date'])
        self.book_instance.refresh_from_db()

        self.assertEqual(self.book_instance.status, 'a')

    def test_staff_can_return_book_by_book_instance_id(self):
        loan = Loan.objects.create(
            book_instance=self.book_instance,
            reader=self.reader,
            return_date=date.today() + timedelta(days=14),
        )
        self.book_instance.status = 'o'
        self.book_instance.save(update_fields=['status'])

        self.client.login(username='librarian', password='pass12345')
        response = self.client.post(reverse('loans:return_book', args=[self.book_instance.pk]))

        self.book_instance.refresh_from_db()
        loan.refresh_from_db()

        self.assertRedirects(response, reverse('catalog:book_detail', args=[self.book.pk]))
        self.assertEqual(self.book_instance.status, 'a')
        self.assertEqual(loan.actual_return_date, date.today())

    def test_non_staff_cannot_return_book(self):
        Loan.objects.create(
            book_instance=self.book_instance,
            reader=self.reader,
            return_date=date.today() + timedelta(days=14),
        )
        self.book_instance.status = 'o'
        self.book_instance.save(update_fields=['status'])

        self.client.login(username='reader', password='pass12345')
        response = self.client.post(reverse('loans:return_book', args=[self.book_instance.pk]))

        self.book_instance.refresh_from_db()

        self.assertRedirects(response, reverse('catalog:index'))
        self.assertEqual(self.book_instance.status, 'o')

    def test_loan_is_overdue_only_for_active_past_due_loans(self):
        overdue_loan = Loan.objects.create(
            book_instance=self.book_instance,
            reader=self.reader,
            return_date=date.today() - timedelta(days=1),
        )
        returned_loan = Loan.objects.create(
            book_instance=BookInstance.objects.create(
                book=self.book,
                inv_number='INV-002',
                status='a',
            ),
            reader=self.reader,
            return_date=date.today() - timedelta(days=2),
            actual_return_date=date.today(),
        )

        self.assertTrue(overdue_loan.is_overdue)
        self.assertFalse(returned_loan.is_overdue)

    def test_staff_can_view_report_of_books_on_loan(self):
        active_loan = Loan.objects.create(
            book_instance=self.book_instance,
            reader=self.reader,
            return_date=date.today() + timedelta(days=7),
        )
        returned_loan = Loan.objects.create(
            book_instance=BookInstance.objects.create(
                book=self.book,
                inv_number='INV-003',
                status='a',
            ),
            reader=self.reader,
            return_date=date.today(),
            actual_return_date=date.today(),
        )

        self.client.login(username='librarian', password='pass12345')
        response = self.client.get(reverse('loans:on_loan_report'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.context['loans']), [active_loan])
        self.assertNotIn(returned_loan, response.context['loans'])

    def test_staff_can_view_report_of_overdue_books(self):
        overdue_loan = Loan.objects.create(
            book_instance=self.book_instance,
            reader=self.reader,
            return_date=date.today() - timedelta(days=5),
        )
        regular_loan = Loan.objects.create(
            book_instance=BookInstance.objects.create(
                book=self.book,
                inv_number='INV-004',
                status='o',
            ),
            reader=self.reader,
            return_date=date.today() + timedelta(days=3),
        )

        self.client.login(username='librarian', password='pass12345')
        response = self.client.get(reverse('loans:overdue_report'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.context['loans']), [overdue_loan])
        self.assertNotIn(regular_loan, response.context['loans'])

    def test_non_staff_cannot_view_reports(self):
        self.client.login(username='reader', password='pass12345')

        response = self.client.get(reverse('loans:on_loan_report'))

        self.assertRedirects(response, reverse('catalog:index'))

        response = self.client.get(reverse('loans:overdue_report'))

        self.assertRedirects(response, reverse('catalog:index'))

    def test_staff_can_return_book_from_on_loan_report(self):
        loan = Loan.objects.create(
            book_instance=self.book_instance,
            reader=self.reader,
            return_date=date.today() + timedelta(days=7),
        )
        self.book_instance.status = 'o'
        self.book_instance.save(update_fields=['status'])

        self.client.login(username='librarian', password='pass12345')
        response = self.client.post(
            reverse('loans:return_book', args=[self.book_instance.pk]),
            {'next': reverse('loans:on_loan_report')},
        )

        self.book_instance.refresh_from_db()
        loan.refresh_from_db()

        self.assertRedirects(response, reverse('loans:on_loan_report'))
        self.assertEqual(self.book_instance.status, 'a')
        self.assertEqual(loan.actual_return_date, date.today())

    def test_return_book_ignores_unsafe_next_url(self):
        loan = Loan.objects.create(
            book_instance=self.book_instance,
            reader=self.reader,
            return_date=date.today() + timedelta(days=7),
        )
        self.book_instance.status = 'o'
        self.book_instance.save(update_fields=['status'])

        self.client.login(username='librarian', password='pass12345')
        response = self.client.post(
            reverse('loans:return_book', args=[self.book_instance.pk]),
            {'next': 'https://example.com/not-safe'},
        )

        loan.refresh_from_db()

        self.assertRedirects(response, reverse('catalog:book_detail', args=[self.book.pk]))
        self.assertEqual(loan.actual_return_date, date.today())
