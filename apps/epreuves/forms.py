from django import forms
from .models import Epreuve, Matiere, Niveau


class EpreuveForm(forms.ModelForm):
    class Meta:
        model = Epreuve
        fields = ['titre', 'matiere', 'niveau', 'type_examen', 'annee', 'fichier', 'corrige', 'description']
        widgets = {
            'titre': forms.TextInput(attrs={'class': 'form-control'}),
            'matiere': forms.Select(attrs={'class': 'form-select'}),
            'niveau': forms.Select(attrs={'class': 'form-select'}),
            'type_examen': forms.Select(attrs={'class': 'form-select'}),
            'annee': forms.NumberInput(attrs={'class': 'form-control', 'min': 1990, 'max': 2030}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class RechercheForm(forms.Form):
    q = forms.CharField(required=False, label="Rechercher",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Titre, matière...'}))
    matiere = forms.ModelChoiceField(queryset=Matiere.objects.all(), required=False,
        empty_label="Toutes les matières", widget=forms.Select(attrs={'class': 'form-select'}))
    niveau = forms.ModelChoiceField(queryset=Niveau.objects.all(), required=False,
        empty_label="Tous les niveaux", widget=forms.Select(attrs={'class': 'form-select'}))
    type_examen = forms.ChoiceField(required=False,
        choices=[('', 'Tous les types')] + Epreuve.TYPES_EXAMEN,
        widget=forms.Select(attrs={'class': 'form-select'}))
    annee = forms.IntegerField(required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Année', 'min': 1990}))
