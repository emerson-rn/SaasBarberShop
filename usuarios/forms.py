from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Usuario

class UsuarioCreationForm(UserCreationForm):
    tipo = forms.ChoiceField(
        choices=Usuario.Tipo.choices,
        label="Tipo de Usuário",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    telefone = forms.CharField(
        max_length=15,
        required=False,
        label="Telefone",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '(00) 00000-0000'})
    )
    email = forms.EmailField(
        required=False,
        label="Email",
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'email@exemplo.com'})
    )

    class Meta:
        model = Usuario
        fields = ('username', 'email', 'tipo', 'telefone', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Nome de usuário'})
        self.fields['password1'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Senha'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Confirmar senha'})

    def save(self, commit=True):
        user = super().save(commit=False)
        user.tipo = self.cleaned_data['tipo']
        user.telefone = self.cleaned_data.get('telefone')
        user.email = self.cleaned_data.get('email')
        if commit:
            user.save()
        return user