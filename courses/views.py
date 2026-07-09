from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import Http404, FileResponse
from courses.models import Lesson, Material
from .models import Lesson

@login_required
def lesson_list(request):
    """Выводит список всех уроков, доступных ученику"""

    # Магия Django ORM: ищем уроки, чей уровень привязан к группе,
    # в которой состоит текущий пользователь (request.user).
    # distinct() нужен, чтобы уроки не дублировались, если ученик вдруг в двух группах одного уровня.
    lessons = Lesson.objects.filter(level__groups__students=request.user)

    # ДОБАВЬ ЭТИ СТРОКИ:
    print(f"DEBUG: Пользователь: {request.user}")
    print(f"DEBUG: Найдено уроков: {lessons.count()}")

    return render(request, 'courses/lesson_list.html', {'lessons': lessons})


@login_required
def lesson_detail(request, lesson_id):
    lesson = get_object_or_404(Lesson, pk=lesson_id)
    return render(request, 'courses/lesson_detail.html', {'lesson': lesson})


@login_required
def download_material(request, material_id):
    """
    Проверяет права доступа и отдает файл
    """
    # 1. Ищем материал, но СТРОГО с проверкой прав доступа!
    # Если чужой ученик попытается подставить ID материала из другой группы,
    # запрос вернет 404 Not Found.
    material = get_object_or_404(
        Material,
        id=material_id,
        lesson__level__groups__students=request.user,
        material_type='pdf'  # Убеждаемся, что запрашивают именно файл
    )

    # 2. Проверяем, прикреплен ли физически файл к объекту базы
    if not material.file:
        raise Http404("Файл не найден на сервере")

    # 3. Открываем файл для чтения ('rb' - read binary)
    file_handle = material.file.open('rb')

    # 4. Отдаем файл браузеру
    # as_attachment=True заставит браузер скачать файл, а не открывать его в новой вкладке
    # filename позволяет задать красивое имя скачиваемого файла
    return FileResponse(
        file_handle,
        as_attachment=True,
        filename=f"Урок_{material.lesson.order}_{material.title}.pdf"
    )