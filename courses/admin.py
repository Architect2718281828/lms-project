from django.contrib import admin
from .models import LanguageLevel, StudentGroup, Lesson, Material


@admin.register(LanguageLevel)
class LanguageLevelAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(StudentGroup)
class StudentGroupAdmin(admin.ModelAdmin):
    # Что показываем в общем списке
    list_display = ('name', 'level', 'start_date')
    # Добавляем боковую панель для фильтрации по уровню
    list_filter = ('level',)
    search_fields = ('name',)

    # Очень важная настройка для ManyToMany полей.
    # Делает выбор учеников в виде удобного виджета с двумя колонками.
    filter_horizontal = ('students',)


# Создаем Inline-класс для Материалов
class MaterialInline(admin.TabularInline):
    model = Material
    extra = 1  # Сколько пустых строк для добавления материалов показывать по умолчанию
    fields = ('title', 'material_type', 'file', 'url')


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    # Отображаем номер урока, название и к какому уровню он относится
    list_display = ('level', 'order', 'title')
    list_filter = ('level',)
    search_fields = ('title',)

    # Подключаем материалы прямо внутрь страницы урока
    inlines = [MaterialInline]


@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    # Отдельная страница для всех материалов, если нужно найти конкретный файл
    list_display = ('title', 'material_type', 'lesson')
    list_filter = ('material_type', 'lesson__level')  # Фильтр по типу и по уровню языка
    search_fields = ('title',)