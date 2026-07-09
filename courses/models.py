from django.db import models
from django.contrib.auth.models import User


class LanguageLevel(models.Model):
    """Уровни владения языком (A1, A2, B1 и т.д.)"""
    name = models.CharField(max_length=50, verbose_name="Название уровня")
    description = models.TextField(blank=True, verbose_name="Описание")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Уровень языка"
        verbose_name_plural = "Уровни языка"


class StudentGroup(models.Model):
    """Группы учеников"""
    name = models.CharField(max_length=100, verbose_name="Название группы")
    level = models.ForeignKey(LanguageLevel, on_delete=models.PROTECT, related_name="groups", verbose_name="Уровень")
    students = models.ManyToManyField(User, related_name="student_groups", verbose_name="Ученики", blank=True)

    # Можно добавить расписание, дату старта и т.д.
    start_date = models.DateField(null=True, blank=True, verbose_name="Дата начала занятий")

    def __str__(self):
        return f"{self.name} ({self.level.name})"

    class Meta:
        verbose_name = "Группа"
        verbose_name_plural = "Группы"


class Lesson(models.Model):
    """Конкретный урок в рамках уровня"""
    level = models.ForeignKey(LanguageLevel, on_delete=models.CASCADE, related_name="courses", verbose_name="Уровень")
    order = models.PositiveIntegerField(verbose_name="Номер урока по счету")
    title = models.CharField(max_length=200, verbose_name="Тема урока")
    description = models.TextField(blank=True, verbose_name="Описание/План урока")

    def __str__(self):
        return f"Урок {self.order}: {self.title} ({self.level.name})"

    class Meta:
        verbose_name = "Урок"
        verbose_name_plural = "Уроки"
        ordering = ['level', 'order']  # Уроки всегда будут выводиться по порядку


class Material(models.Model):
    """Материалы, прикрепленные к уроку (видео, игры, учебники)"""

    # Варианты типов материалов для удобной фильтрации
    MATERIAL_TYPES = [
        ('pdf', 'Учебник / PDF'),
        ('video', 'Видео'),
        ('game', 'Интерактивная игра'),
        ('link', 'Внешняя ссылка'),
    ]

    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name="materials", verbose_name="Урок")
    title = models.CharField(max_length=200, verbose_name="Название материала")
    material_type = models.CharField(max_length=20, choices=MATERIAL_TYPES, verbose_name="Тип контента")

    # Для файлов (PDF), которые загружаются прямо на сервер/S3
    file = models.FileField(upload_to="materials/files/", blank=True, null=True, verbose_name="Файл")

    # Для видео (Youtube/Vimeo) или HTML-игр (GameMaker)
    url = models.URLField(blank=True, null=True, verbose_name="Ссылка (Видео/Игра)")

    def __str__(self):
        return f"{self.get_material_type_display()}: {self.title}"

    class Meta:
        verbose_name = "Материал"
        verbose_name_plural = "Материалы"