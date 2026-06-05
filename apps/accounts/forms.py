from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Utilisateur


class ConnexionForm(forms.Form):
    username = forms.CharField(
        label="Nom d'utilisateur",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Nom d'utilisateur"})
    )
    password = forms.CharField(
        label="Mot de passe",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Mot de passe'})
    )


class InscriptionForm(UserCreationForm):
    first_name = forms.CharField(label="Prénom", required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(label="Nom", required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(label="Email",
        widget=forms.EmailInput(attrs={'class': 'form-control'}))
    role = forms.ChoiceField(
        label="Rôle",
        choices=[('eleve', 'Élève'), ('enseignant', 'Enseignant')],
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    classe = forms.CharField(label="Classe / Filière", required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Terminale D, Licence 2...'}))
    etablissement = forms.CharField(label="Établissement", required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = Utilisateur
        fields = ['username', 'first_name', 'last_name', 'email', 'role', 'classe', 'etablissement', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if not field.widget.attrs.get('class'):
                field.widget.attrs['class'] = 'form-control'


class ProfilForm(forms.ModelForm):
    class Meta:
        model = Utilisateur
        fields = ['first_name', 'last_name', 'email', 'telephone', 'classe', 'etablissement', 'avatar']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'telephone': forms.TextInput(attrs={'class': 'form-control'}),
            'classe': forms.TextInput(attrs={'class': 'form-control'}),
            'etablissement': forms.TextInput(attrs={'class': 'form-control'}),
        }
