from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.conf import settings
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


CLASSES_ELEVE = [
    ('', '-- Choisir une classe --'),
    # Collège
    ('6ème', '6ème'),
    ('5ème', '5ème'),
    ('4ème', '4ème'),
    ('3ème', '3ème'),
    # Lycée
    ('2nde', '2nde'),
    ('1ère A', '1ère A'),
    ('1ère C', '1ère C'),
    ('1ère D', '1ère D'),
    ('1ère TI', '1ère TI'),
    ('Tle A', 'Terminale A'),
    ('Tle C', 'Terminale C'),
    ('Tle D', 'Terminale D'),
    ('Tle TI', 'Terminale TI'),
    # Supérieur
    ('Licence 1', 'Licence 1'),
    ('Licence 2', 'Licence 2'),
    ('Licence 3', 'Licence 3'),
    ('Master 1', 'Master 1'),
    ('Master 2', 'Master 2'),
    ('Autre', 'Autre'),
]

MATIERES_ENSEIGNANT = [
    ('', '-- Choisir une matière --'),
    ('Mathématiques', 'Mathématiques'),
    ('Physique-Chimie', 'Physique-Chimie'),
    ('Sciences de la Vie et de la Terre', 'Sciences de la Vie et de la Terre'),
    ('Français', 'Français'),
    ('Anglais', 'Anglais'),
    ('Histoire-Géographie', 'Histoire-Géographie'),
    ('Philosophie', 'Philosophie'),
    ('Économie', 'Économie'),
    ('Informatique', 'Informatique'),
    ('Éducation Physique', 'Éducation Physique'),
    ('Arts', 'Arts'),
    ('Autre', 'Autre'),
]


class InscriptionEleveForm(UserCreationForm):
    """Formulaire d'inscription réservé aux élèves."""

    first_name = forms.CharField(
        label="Prénom", required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Votre prénom'})
    )
    last_name = forms.CharField(
        label="Nom", required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Votre nom'})
    )
    email = forms.EmailField(
        label="Email", required=False,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'exemple@email.com'})
    )
    telephone = forms.CharField(
        label="Téléphone", required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '6XX XXX XXX'})
    )
    classe = forms.ChoiceField(
        label="Classe", required=True,
        choices=CLASSES_ELEVE,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    etablissement = forms.CharField(
        label="Établissement", required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom de votre établissement'})
    )

    class Meta:
        model = Utilisateur
        fields = ['username', 'first_name', 'last_name', 'email', 'telephone',
                  'classe', 'etablissement', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': "Choisissez un identifiant unique"
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Appliquer form-control à tous les champs non définis
        for name, field in self.fields.items():
            if not field.widget.attrs.get('class'):
                field.widget.attrs['class'] = 'form-control'
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control', 'placeholder': 'Choisissez un mot de passe'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control', 'placeholder': 'Répétez le mot de passe'
        })

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'eleve'
        if commit:
            user.save()
        return user


class InscriptionEnseignantForm(UserCreationForm):
    """Formulaire d'inscription réservé aux enseignants — protégé par code."""

    first_name = forms.CharField(
        label="Prénom", required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Votre prénom'})
    )
    last_name = forms.CharField(
        label="Nom", required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Votre nom'})
    )
    email = forms.EmailField(
        label="Email professionnel", required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'email.pro@etablissement.cm'})
    )
    telephone = forms.CharField(
        label="Téléphone", required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '6XX XXX XXX'})
    )
    matiere_principale = forms.ChoiceField(
        label="Matière enseignée", required=True,
        choices=MATIERES_ENSEIGNANT,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    etablissement = forms.CharField(
        label="Établissement", required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Lycée / Collège / Université...'})
    )
    code_activation = forms.CharField(
        label="Code d'activation enseignant", required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Code fourni par l\'administrateur'
        }),
        help_text="Ce code vous a été fourni par l'administrateur de la plateforme."
    )

    class Meta:
        model = Utilisateur
        fields = ['username', 'first_name', 'last_name', 'email', 'telephone',
                  'matiere_principale', 'etablissement', 'password1', 'password2', 'code_activation']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': "Choisissez un identifiant unique"
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if not field.widget.attrs.get('class'):
                field.widget.attrs['class'] = 'form-control'
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control', 'placeholder': 'Choisissez un mot de passe'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control', 'placeholder': 'Répétez le mot de passe'
        })

    def clean_code_activation(self):
        code = self.cleaned_data.get('code_activation', '').strip()
        code_attendu = getattr(settings, 'CODE_ENSEIGNANT', 'KEYCE2025')
        if code != code_attendu:
            raise forms.ValidationError(
                "Code d'activation incorrect. Contactez l'administrateur."
            )
        return code

    def clean_matiere_principale(self):
        matiere = self.cleaned_data.get('matiere_principale', '')
        if not matiere:
            raise forms.ValidationError("Veuillez choisir votre matière.")
        return matiere

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'enseignant'
        # Stocker la matière dans le champ classe (réutilisation du champ existant)
        user.classe = self.cleaned_data.get('matiere_principale', '')
        if commit:
            user.save()
        return user


# Garder l'ancien pour compatibilité
class InscriptionForm(InscriptionEleveForm):
    pass


class ProfilForm(forms.ModelForm):
    class Meta:
        model = Utilisateur
        fields = ['first_name', 'last_name', 'email', 'telephone', 'classe', 'etablissement', 'avatar']
        widgets = {
            'first_name':    forms.TextInput(attrs={'class': 'form-control'}),
            'last_name':     forms.TextInput(attrs={'class': 'form-control'}),
            'email':         forms.EmailInput(attrs={'class': 'form-control'}),
            'telephone':     forms.TextInput(attrs={'class': 'form-control'}),
            'classe':        forms.TextInput(attrs={'class': 'form-control'}),
            'etablissement': forms.TextInput(attrs={'class': 'form-control'}),
        }
