from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Reader


class ReaderRegistrationForm(UserCreationForm):
    ticket_number = forms.CharField(label='Номер читательского билета', max_length=20)
    phone = forms.CharField(label='Номер телефона', max_length=20)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('first_name', 'last_name', 'email')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault('class', 'form-control')
        self.fields['username'].label = 'Логин'
        self.fields['first_name'].label = 'Имя'
        self.fields['last_name'].label = 'Фамилия'
        self.fields['email'].label = 'Электронная почта'
        self.fields['password1'].label = 'Пароль'
        self.fields['password2'].label = 'Подтверждение пароля'

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            Reader.objects.create(
                user=user,
                ticket_number=self.cleaned_data['ticket_number'],
                phone=self.cleaned_data['phone'],
            )
        return user
