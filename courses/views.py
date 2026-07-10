from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.http import Http404, FileResponse
from .models import Lesson, Material
from .forms import CustomUserCreationForm

def approval_pending(request):
    # Если пользователь авторизован и админ его уже подтвердил — возвращаем на уроки
    if request.user.is_authenticated and request.user.is_approved:
        return redirect('lesson_list')
    return render(request, 'registration/approval_pending.html')

@login_required
def profile_view(request):
    # Защита от неподтвержденных пользователей
    if not request.user.is_approved and not request.user.is_staff:
        return redirect('approval_pending')
    return render(request, 'courses/profile.html', {'user': request.user})

def register_view(request):
    if request.user.is_authenticated:
        return redirect('lesson_list')

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('lesson_list')
    else:
        form = CustomUserCreationForm()

    return render(request, 'registration/register.html', {'form': form})

@login_required
def lesson_list(request):
    # Защита от неподтвержденных пользователей
    if not request.user.is_approved and not request.user.is_staff:
        return redirect('approval_pending')

    query = request.GET.get('q')  # Получаем поисковый запрос из строки адреса[cite: 6]

    # Если зашел студент — показываем материалы ТОЛЬКО тех уровней, к группам которых он привязан
    if hasattr(request.user, 'role') and request.user.role == 'student':
        lessons = Lesson.objects.filter(level__groups__students=request.user).distinct()
    else:
        # Администраторы, сотрудники и преподаватели видят всё без ограничений
        lessons = Lesson.objects.all()

    if query:
        # Фильтруем: ищем в заголовке (icontains игнорирует регистр)[cite: 6]
        lessons = lessons.filter(title__icontains=query)

    return render(request, 'courses/lesson_list.html', {'lessons': lessons, 'query': query})

@login_required
def lesson_detail(request, lesson_id):
    # Защита от неподтвержденных пользователей
    if not request.user.is_approved and not request.user.is_staff:
        return redirect('approval_pending')

    lesson = get_object_or_404(Lesson, pk=lesson_id)

    # Защита от ручного ввода URL-адреса: проверяем, имеет ли право студент смотреть этот уровень
    if hasattr(request.user, 'role') and request.user.role == 'student':
        has_access = lesson.level.groups.filter(students=request.user).exists()
        if not has_access:
            return redirect('lesson_list')

    return render(request, 'courses/lesson_detail.html', {'lesson': lesson})

@staff_member_required(login_url='login')
def edit_lesson(request):
    return render(request, 'edit_lesson.html')

@login_required
def download_material(request, material_id):
    # Защита от неподтвержденных пользователей
    if not request.user.is_approved and not request.user.is_staff:
        return redirect('approval_pending')

    # Если скачивает студент, проверяем его жесткую привязку к группе через материалы[cite: 6]
    if hasattr(request.user, 'role') and request.user.role == 'student':
        material = get_object_or_404(
            Material,
            id=material_id,
            lesson__level__groups__students=request.user,
            material_type='pdf'
        )
    else:
        # Персонал может скачивать любые файлы уроков
        material = get_object_or_404(Material, id=material_id, material_type='pdf')

    if not material.file:
        raise Http404("Файл не найден на сервере")[cite: 6]

    file_handle = material.file.open('rb')[cite: 6]

    return FileResponse(
        file_handle,
        as_attachment=True,
        filename=f"Урок_{material.lesson.order}_{material.title}.pdf"
    )[cite: 6]