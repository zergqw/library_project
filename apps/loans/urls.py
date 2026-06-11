from django.urls import path

from . import views

app_name = 'loans'

urlpatterns = [
    path('book/<int:pk>/borrow', views.borrow_book, name='borrow_book'),
    path('book/<int:pk>/return', views.return_book, name='return_book'),
    path('reports/on-loan/', views.on_loan_report, name='on_loan_report'),
    path('reports/overdue/', views.overdue_report, name='overdue_report'),
]
