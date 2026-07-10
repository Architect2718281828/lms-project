from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Главная админка Django
    path('admin/', admin.site.urls),

    # Подключаем все маршруты приложения к корню сайта (здесь теперь лежит и главная, и логин)
    path('', include('courses.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)