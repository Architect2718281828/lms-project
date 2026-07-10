from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
# Импортируем класс для перенаправления страниц
from django.views.generic import RedirectView

urlpatterns = [
    # Главная админка Django
    path('admin/', admin.site.urls),

    # Если пользователь заходит на чистый домен "", плавно перекидываем его на "/lessons/"
    path('', RedirectView.as_view(url='lessons/', permanent=True)),

    # Подключаем все маршруты приложения к корню сайта
    path('', include('courses.urls')),
]

# Добавляем эти строки для корректной работы медиафайлов в режиме DEBUG
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)