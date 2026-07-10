from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser, LanguageLevel

class CustomUserCreationForm(UserCreationForm):
    level = forms.ModelChoiceField(
        queryset=LanguageLevel.objects.all(),
        required=False,
        label='Уровень языка',
        empty_label='Выберите уровень'
    )

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('email', 'first_name', 'last_name', 'role', 'level')

    def clean(self):
        cleaned_data = super().clean()
        role = cleaned_data.get("role")
        level = cleaned_data.get("level")

        if role == 'student' and not level:
            self.add_error('level', "Студенты обязаны выбрать уровень языка!")
        return cleaned_data

class CustomAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(
        label="Электронная почта",
        widget=forms.EmailInput(attrs={'autofocus': True, 'placeholder': 'name@example.com'})
    )
    password = forms.CharField(
        label="Пароль",
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'current-password'})
    )