from datetime import date, timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from apps.catalog.models import BookInstance
from apps.users.models import Reader

from .models import Loan


def _staff_guard(request):
    if request.user.is_staff:
        return None

    messages.error(request, 'У вас нет прав для просмотра этого раздела.')
    return redirect('catalog:index')


def _safe_next_url(request):
    next_url = request.POST.get('next') or request.GET.get('next')
    if not next_url:
        return None

    if url_has_allowed_host_and_scheme(
        next_url,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        return next_url
    return None


@login_required
@require_POST
def borrow_book(request, pk):
    reader = get_object_or_404(Reader, user=request.user)

    with transaction.atomic():
        book_instance = get_object_or_404(BookInstance.objects.select_for_update(), pk=pk)

        if book_instance.status != 'a':
            messages.error(request, 'Эта копия уже недоступна.')
            return redirect('catalog:book_detail', pk=book_instance.book.pk)

        due_date = date.today() + timedelta(days=14)
        Loan.objects.create(
            book_instance=book_instance,
            reader=reader,
            loan_date=date.today(),
            return_date=due_date,
        )

        book_instance.status = 'o'
        book_instance.save(update_fields=['status'])

    messages.success(
        request,
        f"Книга '{book_instance.book.title}' закреплена за вами до {due_date.strftime('%d.%m.%Y')}.",
    )
    return redirect('catalog:book_detail', pk=book_instance.book.pk)


@login_required
@require_POST
def return_book(request, pk):
    guard_response = _staff_guard(request)
    if guard_response:
        return guard_response

    with transaction.atomic():
        book_instance = get_object_or_404(BookInstance.objects.select_for_update(), pk=pk)
        loan = (
            Loan.objects.select_for_update()
            .filter(book_instance=book_instance, actual_return_date__isnull=True)
            .first()
        )

        if loan is None:
            messages.error(request, 'Для этого экземпляра не найдена активная выдача.')
            redirect_to = _safe_next_url(request)
            if redirect_to:
                return redirect(redirect_to)
            return redirect('catalog:book_detail', pk=book_instance.book.pk)

        loan.actual_return_date = date.today()
        loan.save(update_fields=['actual_return_date'])

        book_instance.status = 'a'
        book_instance.save(update_fields=['status'])

    messages.success(request, f"Книга '{book_instance.book.title}' успешно возвращена.")
    redirect_to = _safe_next_url(request)
    if redirect_to:
        return redirect(redirect_to)
    return redirect('catalog:book_detail', pk=book_instance.book.pk)


@login_required
def on_loan_report(request):
    guard_response = _staff_guard(request)
    if guard_response:
        return guard_response

    loans = (
        Loan.objects.filter(actual_return_date__isnull=True)
        .select_related('reader__user', 'book_instance__book')
        .order_by('return_date', 'loan_date')
    )
    return render(
        request,
        'loans/on_loan_report.html',
        {
            'title': 'Книги на руках',
            'loans': loans,
        },
    )


@login_required
def overdue_report(request):
    guard_response = _staff_guard(request)
    if guard_response:
        return guard_response

    loans = [
        loan
        for loan in (
            Loan.objects.filter(actual_return_date__isnull=True)
            .select_related('reader__user', 'book_instance__book')
            .order_by('return_date', 'loan_date')
        )
        if loan.is_overdue
    ]
    return render(
        request,
        'loans/overdue_report.html',
        {
            'title': 'Просроченные книги',
            'loans': loans,
        },
    )
