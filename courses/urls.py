from django.urls import path
from . import views

urlpatterns = [
    # Список всех уроков
    path('lessons/', views.lesson_list, name='lesson_list'),

    # Страница конкретного урока
    path('lessons/<int:lesson_id>/', views.lesson_detail, name='lesson_detail'),

    # Скачивание файла (материала)
    path('materials/<int:material_id>/download/', views.download_material, name='download_material'),
]