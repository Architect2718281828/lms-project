from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.http import Http404, FileResponse
from .models import Lesson, Material
from .forms import CustomUserCreationForm

@login_required
def profile_view(request):
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
    query = request.GET.get('q')  # Получаем поисковый запрос из строки адреса
    lessons = Lesson.objects.all()  # Берем все уроки

    if query:
        # Фильтруем: ищем в заголовке (icontains игнорирует регистр)
        lessons = lessons.filter(title__icontains=query)

    return render(request, 'courses/lesson_list.html', {'lessons': lessons, 'query': query})

@login_required
def lesson_detail(request, lesson_id):
    lesson = get_object_or_404(Lesson, pk=lesson_id)
    return render(request, 'courses/lesson_detail.html', {'lesson': lesson})

@staff_member_required(login_url='login')
def edit_lesson(request):
    return render(request, 'edit_lesson.html')

@login_required
def download_material(request, material_id):
    material = get_object_or_404(
        Material,
        id=material_id,
        lesson__level__groups__students=request.user,
        material_type='pdf'
    )

    if not material.file:
        raise Http404("Файл не найден на сервере")

    file_handle = material.file.open('rb')

    return FileResponse(
        file_handle,
        as_attachment=True,
        filename=f"Урок_{material.lesson.order}_{material.title}.pdf"
    )