from django.contrib import admin
from .models import CustomUser, LanguageLevel, StudentGroup, Lesson, Material

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('email', 'first_name', 'last_name', 'role', 'is_approved')

    def save_model(self, request, obj, form, change):
        # Хэшируем пароль ТОЛЬКО если он был изменен в форме
        if 'password' in form.changed_data:
            obj.set_password(form.cleaned_data['password'])
        super().save_model(request, obj, form, change)

@admin.register(LanguageLevel)
class LanguageLevelAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(StudentGroup)
class StudentGroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'level', 'start_date')
    list_filter = ('level',)
    search_fields = ('name',)
    filter_horizontal = ('students',)

class MaterialInline(admin.TabularInline):
    model = Material
    extra = 1
    fields = ('title', 'material_type', 'file', 'url')

@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('level', 'order', 'title')
    list_filter = ('level',)
    search_fields = ('title',)
    inlines = [MaterialInline]

@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = ('title', 'material_type', 'lesson')
    list_filter = ('material_type', 'lesson__level')
    search_fields = ('title',)