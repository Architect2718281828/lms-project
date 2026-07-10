from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .forms import CustomAuthenticationForm

urlpatterns = [
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

    # Уроки и материалы (ТЕПЕРЬ ЭТО ГЛАВНАЯ СТРАНИЦА)
    path('', views.lesson_list, name='lesson_list'),

    # Детали урока оставляем без изменений
    path('lessons/<int:lesson_id>/', views.lesson_detail, name='lesson_detail'),
    path('materials/<int:material_id>/download/', views.download_material, name='download_material'),
]