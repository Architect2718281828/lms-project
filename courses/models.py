import os
from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.files.storage import FileSystemStorage
from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver


# 1. ЗАЩИЩЕННОЕ ХРАНИЛИЩЕ (В самом верху, без дубликатов)
class OverwriteStorage(FileSystemStorage):
    def get_available_name(self, name, max_length=None):
        if self.exists(name):
            try:
                os.remove(os.path.join(self.location, name))
            except PermissionError:
                # Если Windows заблокировал файл дескриптором, просто пропускаем
                pass
        return super().get_available_name(name, max_length)


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email является обязательным полем')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Суперпользователь должен иметь is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Суперпользователь должен иметь is_superuser=True.')

        return self.create_user(email, password, **extra_fields)


class LanguageLevel(models.Model):
    name = models.CharField(max_length=50, verbose_name="Название уровня")
    description = models.TextField(blank=True, verbose_name="Описание")

    def __str__(self):
        return self.name


class CustomUser(AbstractUser):
    username = None
    email = models.EmailField('Email', unique=True)
    first_name = models.CharField('Имя', max_length=50)
    last_name = models.CharField('Фамилия', max_length=50)

    ROLE_CHOICES = [
        ('student', 'Студент'),
        ('employee', 'Сотрудник')
    ]
    role = models.CharField('Роль', max_length=10, choices=ROLE_CHOICES, default='student')
    level = models.ForeignKey(LanguageLevel, on_delete=models.SET_NULL, blank=True, null=True,
                              verbose_name='Уровень языка')
    is_approved = models.BooleanField('Подтвержден администратором', default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    def __str__(self):
        return self.email


class StudentGroup(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название группы")
    level = models.ForeignKey(LanguageLevel, on_delete=models.PROTECT, related_name="groups", verbose_name="Уровень")
    students = models.ManyToManyField(CustomUser, related_name="student_groups", verbose_name="Ученики", blank=True)
    start_date = models.DateField(null=True, blank=True, verbose_name="Дата начала занятий")

    def __str__(self):
        return f"{self.name} ({self.level.name})"

    class Meta:
        verbose_name = "Группа"
        verbose_name_plural = "Группы"


class Lesson(models.Model):
    level = models.ForeignKey(LanguageLevel, on_delete=models.CASCADE, related_name="courses", verbose_name="Уровень")
    order = models.PositiveIntegerField(verbose_name="Номер урока по счету")
    title = models.CharField(max_length=200, verbose_name="Тема урока")
    description = models.TextField(blank=True, verbose_name="Описание/План урока")

    def __str__(self):
        return f"Урок {self.order}: {self.title} ({self.level.name})"

    class Meta:
        verbose_name = "Урок"
        verbose_name_plural = "Уроки"
        ordering = ['level', 'order']


class Material(models.Model):
    MATERIAL_TYPES = [
        ('pdf', 'Учебник / PDF'),
        ('video', 'Видео'),
        ('game', 'Интерактивная игра'),
        ('link', 'Внешняя ссылка'),
    ]

    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name="materials", verbose_name="Урок")
    title = models.CharField(max_length=200, verbose_name="Название материала")
    material_type = models.CharField(max_length=20, choices=MATERIAL_TYPES, verbose_name="Тип контента")
    file = models.FileField(
        upload_to="materials/files/",
        storage=OverwriteStorage(),
        blank=True,
        null=True,
        verbose_name="Файл"
    )
    url = models.URLField(blank=True, null=True, verbose_name="Ссылка (Видео/Игра)")

    def __str__(self):
        return f"{self.get_material_type_display()}: {self.title}"

    class Meta:
        verbose_name = "Material"
        verbose_name_plural = "Материалы"


# 2. ЗАЩИЩЕННЫЕ СИГНАЛЫ (В самом конце, вызываются строго по одному разу)

@receiver(post_delete, sender=Material)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    if instance.file:
        if os.path.isfile(instance.file.path):
            try:
                os.remove(instance.file.path)
            except PermissionError:
                pass


@receiver(pre_save, sender=Material)
def auto_delete_file_on_change(sender, instance, **kwargs):
    if not instance.pk:
        return False

    try:
        old_file = sender.objects.get(pk=instance.pk).file
    except sender.DoesNotExist:
        return False

    new_file = instance.file
    if not old_file == new_file:
        if old_file and os.path.isfile(old_file.path):
            try:
                os.remove(old_file.path)
            except PermissionError:
                pass