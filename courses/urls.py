from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .forms import CustomAuthenticationForm

urlpatterns = [
    # Страница ожидания подтверждения аккаунта
    path('approval-pending/', views.approval_pending, name='approval_pending'),

    # Авторизация
    path('login/', auth_views.LoginView.as_view(
        template_name='registration/login.html',
        authentication_form=CustomAuthenticationForm,
        redirect_authenticated_user=True
    ), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    # Регистрация
    path('register/', views.register_view, name='register'),

    # Профиль
    path('profile/', views.profile_view, name='profile'),

    # ВЕРНУЛИ СТАРЫЙ ПУТЬ
    path('lessons/', views.lesson_list, name='lesson_list'),

    # Детали урока и скачивание файлов
    path('lessons/<int:lesson_id>/', views.lesson_detail, name='lesson_detail'),
    path('materials/<int:material_id>/download/', views.download_material, name='download_material'),
]