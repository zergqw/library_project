from django.urls import path

from . import views

app_name = 'catalog'

urlpatterns = [
    path('', views.index, name='index'),
    path('books/', views.book_list, name='book_list'),
    path('books/<int:pk>/', views.book_detail, name='book_detail'),
    path('authors/', views.author_list, name='author_list'),
    path('authors/<int:pk>/', views.author_detail, name='author_detail'),
]
