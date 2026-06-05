from django.contrib import admin
from .models import Quiz, Question, Choix, SessionQuiz, ReponseEleve

class ChoixInline(admin.TabularInline):
    model = Choix
    extra = 4

class QuestionInline(admin.StackedInline):
    model = Question
    extra = 2
    show_change_link = True

@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ['titre', 'matiere', 'niveau', 'nb_questions', 'est_actif', 'cree_par']
    list_filter = ['matiere', 'est_actif']
    inlines = [QuestionInline]

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['enonce', 'quiz', 'type_question', 'points']
    inlines = [ChoixInline]

@admin.register(SessionQuiz)
class SessionQuizAdmin(admin.ModelAdmin):
    list_display = ['utilisateur', 'quiz', 'score_obtenu', 'pourcentage', 'statut', 'date_debut']
    list_filter = ['statut', 'date_debut']
    readonly_fields = ['date_debut', 'date_fin']
