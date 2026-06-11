from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import redirect, render

from apps.loans.models import Loan

from .forms import ReaderRegistrationForm
from .models import Reader


@login_required
def profile(request):
    reader = Reader.objects.filter(user=request.user).first()

    if reader is None:
        if request.user.is_staff:
            messages.info(
                request,
                'Для сотрудников профиль читателя не требуется. Продолжайте работу через административную панель.',
            )
            return redirect('admin:index')
        raise Http404('Для пользователя не найден профиль читателя.')

    loans = (
        Loan.objects.filter(reader=reader)
        .select_related('book_instance__book')
        .order_by('-loan_date')
    )

    return render(
        request,
        'users/profile.html',
        {
            'reader': reader,
            'active_loans': loans.filter(actual_return_date__isnull=True),
            'loan_history': loans.filter(actual_return_date__isnull=False),
        },
    )


def signup(request):
    if request.method == 'POST':
        form = ReaderRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Аккаунт для {username} успешно создан. Теперь можно войти в систему.')
            return redirect('login')
    else:
        form = ReaderRegistrationForm()
    return render(request, 'registration/signup.html', {'form': form})
