<div align="center">

<img src="https://img.shields.io/badge/Django-4.2-092E20?style=for-the-badge&logo=django&logoColor=white"/>
<img src="https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white"/>
<img src="https://img.shields.io/badge/MySQL-8.0-4479A1?style=for-the-badge&logo=mysql&logoColor=white"/>
<img src="https://img.shields.io/badge/Bootstrap-5.3-7952B3?style=for-the-badge&logo=bootstrap&logoColor=white"/>
<img src="https://img.shields.io/badge/OpenAI-GPT--3.5-412991?style=for-the-badge&logo=openai&logoColor=white"/>

# 🎓 EDUAI Cameroun
### Plateforme Éducative Intelligente

*Bibliothèque d'épreuves · Quiz interactif · Correction IA · Monitoring réseau · Sécurité*

**Projet Tuteuré — Bachelor 1 Informatique & IA · 2025**

</div>

---

## 📋 Présentation

**EDUAI Cameroun** est une plateforme web éducative déployée en réseau local, conçue pour les établissements scolaires camerounais. Elle centralise les épreuves officielles (BAC, BEPC, Probatoire, Concours), propose des quiz interactifs chronométrés, intègre un module d'intelligence artificielle pédagogique (correction automatique, chatbot, anti-plagiat) et offre un tableau de bord de monitoring système en temps réel avec journalisation de sécurité.

---

## ✨ Fonctionnalités

### 📚 Bibliothèque d'épreuves
- Dépôt, classement et téléchargement d'épreuves (PDF, DOC, DOCX)
- Recherche multicritères : matière, niveau, type d'examen, année
- Support des corrigés associés
- Statistiques de téléchargement par épreuve

### 🧠 Quiz Interactif
- Chronomètre intégré par quiz
- Types de questions : QCM, Vrai/Faux, Réponse ouverte
- Score, classement et correction détaillée à la fin
- Historique des résultats par élève
- Limite de tentatives configurable

### 🤖 Module Intelligence Artificielle (OpenAI)
- **Correction automatique** : soumettre une réponse → note sur 20 + commentaires pédagogiques
- **EduBot Chatbot** : assistant pédagogique disponible 24h/24, adapté aux programmes camerounais
- **Détection de plagiat** : comparaison de similarité entre deux copies
- Mode démo intégré (sans clé API)

### 📊 Dashboard Monitoring (Admins)
- Métriques système temps réel : CPU, RAM, Disque, Réseau (via `psutil`)
- Graphiques interactifs (Chart.js) : téléchargements/heure, quiz/jour, requêtes IA
- Liste des utilisateurs actifs avec adresse IP et heure de dernière activité
- Journal d'activité en direct
- Actualisation automatique toutes les 10 secondes

### 🔒 Sécurité
- **Anti-brute force** : blocage automatique d'IP après 5 échecs consécutifs (15 min)
- **Détection téléchargements massifs** : alerte si >50 téléchargements en 2 minutes
- **Journal complet** : toutes les actions (connexion, téléchargement, requête IA) tracées
- **Alertes temps réel** : panneau dédié dans le dashboard admin
- **Scripts PowerShell** : configuration et surveillance du pare-feu Windows Defender

### 👥 Gestion des utilisateurs
- Trois rôles : Administrateur · Enseignant · Élève
- Profils complets avec avatar, classe, établissement
- Accès conditionnel selon le rôle

---

## 🛠️ Stack Technique

| Composant | Technologie |
|---|---|
| Backend | Python 3.11 · Django 4.2 |
| Base de données | MySQL 8.0 (via XAMPP) |
| Frontend | HTML5 · CSS3 · Bootstrap 5.3 · JavaScript ES6 |
| Graphiques | Chart.js 4.4 |
| Intelligence Artificielle | OpenAI API (GPT-3.5 Turbo) |
| Monitoring système | psutil 5.9 |
| API REST | Django REST Framework 3.15 |
| Sécurité réseau | Windows Defender Firewall · PowerShell |
| Serveur local | Django dev server · XAMPP (MySQL) |

---

## 🗂️ Structure du projet

```
eduai_cameroun/
│
├── 📁 eduai_cameroun/          # Configuration Django centrale
│   ├── settings.py             # BDD, IA, sécurité, sessions
│   ├── urls.py                 # Routage principal + API REST
│   └── wsgi.py
│
├── 📁 apps/
│   ├── 📁 accounts/            # Authentification & profils utilisateurs
│   │   ├── models.py           # Modèle Utilisateur étendu (rôles)
│   │   ├── views.py            # Connexion, inscription, profil
│   │   ├── forms.py
│   │   ├── urls.py
│   │   ├── api_urls.py         # API REST utilisateurs
│   │   └── admin.py
│   │
│   ├── 📁 epreuves/            # Gestion des épreuves
│   │   ├── models.py           # Epreuve, Matiere, Niveau, Telechargement
│   │   ├── views.py            # Liste, détail, upload, téléchargement sécurisé
│   │   ├── forms.py
│   │   ├── urls.py
│   │   ├── api_urls.py         # API REST épreuves
│   │   └── admin.py
│   │
│   ├── 📁 quiz/                # Système de quiz interactif
│   │   ├── models.py           # Quiz, Question, Choix, SessionQuiz, ReponseEleve
│   │   ├── views.py            # Démarrer, passer, résultats, classement
│   │   ├── urls.py
│   │   ├── api_urls.py
│   │   └── admin.py
│   │
│   ├── 📁 ia/                  # Module Intelligence Artificielle
│   │   ├── views.py            # Correction, chatbot, anti-plagiat (OpenAI)
│   │   └── urls.py
│   │
│   ├── 📁 monitoring/          # Dashboard admin temps réel
│   │   ├── views.py            # Métriques psutil + stats applicatives (JSON)
│   │   └── urls.py
│   │
│   └── 📁 securite/            # Sécurité & journalisation
│       ├── models.py           # TentativeConnexion, LogActivite, AlerteSecurite
│       ├── middleware.py       # BruteForceMiddleware, ActivityLogMiddleware
│       ├── views.py            # Tableau sécurité, déblocage IP, alertes
│       ├── urls.py
│       └── admin.py
│
├── 📁 templates/               # Pages HTML (Bootstrap 5)
│   ├── base.html               # Layout principal + navbar
│   ├── accueil.html            # Page d'accueil + stats
│   ├── 📁 accounts/            # Connexion, inscription, profil
│   ├── 📁 epreuves/            # Liste, détail, upload
│   ├── 📁 quiz/                # Liste, passer, résultat, mes résultats
│   ├── 📁 ia/                  # Interface correction / chatbot / plagiat
│   ├── 📁 monitoring/          # Dashboard graphiques temps réel
│   └── 📁 securite/            # Tableau alertes & logs
│
├── 📁 static/
│   ├── css/style.css           # Feuille de style EDUAI
│   └── js/main.js              # JavaScript principal
│
├── 📁 scripts/
│   ├── setup_db.sql            # Création base MySQL
│   ├── init_data.py            # Données de démonstration
│   ├── configure_firewall.ps1  # Configuration pare-feu Windows
│   └── anti_brute_force.ps1   # Surveillance et blocage IP automatique
│
├── 📁 media/                   # Fichiers uploadés (épreuves)
├── manage.py
├── requirements.txt
├── .env.example
└── README.md
```

---

## 🌐 Architecture Réseau

```
                        RÉSEAU LOCAL 192.168.1.0/24
                        ─────────────────────────────

  ┌──────────────────────────────┐
  │   PC SERVEUR — 192.168.1.10  │  ← Django + MySQL (XAMPP) + PowerShell
  │   Windows 11 Professionnel   │
  │   Windows Defender Firewall  │
  └──────────────┬───────────────┘
                 │  Switch / Routeur Wi-Fi
       ┌─────────┼──────────┬────────────┐
       │         │          │            │
  ┌────┴───┐ ┌───┴────┐ ┌───┴────┐ ┌────┴───┐
  │ .1.20  │ │ .1.30  │ │ .1.31  │ │ .1.32  │
  │ Admin  │ │ Élève 1│ │ Élève 2│ │ Ens.   │
  └────────┘ └────────┘ └────────┘ └────────┘
```

---

## ⚙️ Installation

### Prérequis
- Windows 10/11 avec Python 3.11+
- [XAMPP](https://www.apachefriends.org) (pour MySQL)
- Git

### 1. Cloner le dépôt

```bash
git clone https://github.com/<votre-compte>/eduai-cameroun.git
cd eduai-cameroun
```

### 2. Créer la base de données MySQL

Démarrer XAMPP → Apache + MySQL, puis dans **phpMyAdmin** :

```sql
-- Onglet SQL de phpMyAdmin
CREATE DATABASE eduai_cameroun CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

Ou exécuter directement le script fourni :
```
scripts/setup_db.sql
```

### 3. Environnement Python

```bash
python -m venv venv
venv\Scripts\activate       # Windows
# source venv/bin/activate  # Linux/Mac

pip install -r requirements.txt
```

### 4. Variables d'environnement

Copier `.env.example` → `.env` et remplir les valeurs :

```env
SECRET_KEY=une-cle-secrete-longue-et-aleatoire
DEBUG=True

DB_NAME=eduai_cameroun
DB_USER=root
DB_PASSWORD=
DB_HOST=127.0.0.1
DB_PORT=3306

# Optionnel — mode démo si absent
OPENAI_API_KEY=sk-...

ALERT_EMAIL=admin@votre-etablissement.cm
```

### 5. Migrations et fichiers statiques

```bash
python manage.py migrate
python manage.py collectstatic --noinput
```

### 6. Données de démonstration

```bash
python scripts/init_data.py
```

Crée automatiquement les matières, niveaux, comptes et un quiz de démonstration.

### 7. Lancer le serveur

```bash
# Accessible depuis tout le réseau local
python manage.py runserver 0.0.0.0:80
```

---

## 🔑 Comptes par défaut

> ⚠️ Changer les mots de passe en production.

| Identifiant | Mot de passe | Rôle |
|---|---|---|
| `admin` | `EduAI2025!` | Administrateur |
| `enseignant1` | `EduAI2025!` | Enseignant |
| `eleve1` | `EduAI2025!` | Élève |
| `eleve2` | `EduAI2025!` | Élève |

---

## 🌍 URLs principales

| URL | Description | Accès |
|---|---|---|
| `/` | Accueil | Public |
| `/epreuves/liste/` | Bibliothèque d'épreuves | Public |
| `/epreuves/upload/` | Uploader une épreuve | Enseignant / Admin |
| `/quiz/` | Liste des quiz | Public |
| `/ia/` | Module IA | Connecté |
| `/monitoring/` | Dashboard système | Admin |
| `/securite/` | Tableau de sécurité | Admin |
| `/admin/` | Back-office Django | Admin |

### API REST

| Endpoint | Méthode | Description |
|---|---|---|
| `/api/epreuves/` | GET | Liste des épreuves (JSON) |
| `/api/epreuves/stats/` | GET | Statistiques téléchargements |
| `/api/quiz/` | GET | Liste des quiz |
| `/api/users/` | GET | Liste utilisateurs (admin) |
| `/monitoring/api/metriques/` | GET | CPU, RAM, réseau en temps réel |
| `/monitoring/api/historique/` | GET | Données historiques graphiques |
| `/ia/corriger/` | POST | Correction automatique IA |
| `/ia/chatbot/` | POST | EduBot chatbot |
| `/ia/plagiat/` | POST | Détection de plagiat |

---

## 🔒 Sécurité — Guide rapide

### Configurer le pare-feu Windows (une seule fois, en tant qu'Admin)

```powershell
powershell -ExecutionPolicy Bypass -File scripts\configure_firewall.ps1
```

Ouvre les ports 80 (HTTP) et 8000 (Django dev), restreint MySQL en local uniquement.

### Lancer la surveillance anti-brute force

```powershell
powershell -ExecutionPolicy Bypass -File scripts\anti_brute_force.ps1
```

Surveille les journaux Apache/Django toutes les 30 secondes et bloque automatiquement toute IP dépassant 5 tentatives de connexion échouées via une règle Windows Defender Firewall.

### Paramètres configurables dans `.env` / `settings.py`

```python
MAX_LOGIN_ATTEMPTS = 5           # Tentatives avant blocage
LOCKOUT_DURATION_MINUTES = 15    # Durée du blocage (minutes)
SUSPICIOUS_DOWNLOAD_THRESHOLD = 50  # Seuil d'alerte téléchargements (sur 2 min)
```

---

## 📸 Aperçu des pages

| Page | Description |
|---|---|
| **Accueil** | Hero section + statistiques globales + épreuves récentes + présentation IA |
| **Bibliothèque** | Filtres sidebar + grille de cartes + téléchargement sécurisé |
| **Quiz** | Chronomètre + QCM + progression + soumission avec confirmation |
| **Résultat quiz** | Note, barre de progression, détail par question, classement |
| **Module IA** | 3 onglets : correction / chatbot / anti-plagiat, résultats visuels |
| **Monitoring** | Jauges CPU/RAM/Disque, graphiques Chart.js, table utilisateurs live |
| **Sécurité** | Alertes actives, IPs bloquées, journal d'activité en temps réel |

---

## 🧪 Modèles de données clés

```
Utilisateur (role: admin | enseignant | eleve)
    │
    ├── Epreuve (matiere, niveau, type_examen, annee, fichier)
    │       └── Telechargement (ip, date)
    │
    ├── SessionQuiz ──── Quiz (matiere, niveau, duree)
    │       └── ReponseEleve ──── Question ──── Choix
    │
    ├── LogActivite (type, ip, date, est_suspect)
    └── TentativeConnexion (ip, nb_tentatives, est_bloque)
```

---

## 📦 Dépendances principales

```
Django==4.2.13
mysqlclient==2.2.4
openai==1.30.1
psutil==5.9.8
djangorestframework==3.15.1
django-crispy-forms==2.1
crispy-bootstrap5==0.7
python-dotenv==1.0.1
Pillow==10.3.0
```

---

## 🤝 Contribuer

1. Forker le dépôt
2. Créer une branche : `git checkout -b feature/ma-fonctionnalite`
3. Committer : `git commit -m "feat: description claire"`
4. Pousser : `git push origin feature/ma-fonctionnalite`
5. Ouvrir une Pull Request

---

## 📄 Licence

Projet académique — Usage éducatif uniquement.  
Développé dans le cadre du **Bachelor 1 Informatique & Intelligence Artificielle**,  
**KEYCE Informatique & IA — Yaoundé, Cameroun · 2025**

---

<div align="center">
  <strong>EDUAI Cameroun v1.0</strong> — Plateforme Éducative Intelligente<br>
  <em>Python · Django · MySQL · Bootstrap · OpenAI</em>
</div>

---

## 👥 Équipe projet

> **Bachelor 1 Informatique & Intelligence Artificielle — KEYCE Yaoundé · 2025**

<div align="center">

### 👑 Chef de Projet

| | Nom | Rôle |
|:---:|---|---|
| 🎯 | **DOMCHE DANIELLE** | Chef de Projet — Coordination générale, planification, livrables |

---

### ⚙️ Développement Backend

| | Nom |
|:---:|---|
| 💻 | **ENGUENO RAFAEL** |
| 💻 | **PEH PEH SCOTT** |

> Django · Python · API REST · MySQL · Modèles de données · Middleware sécurité

---

### 🎨 Développement Frontend

| | Nom |
|:---:|---|
| 🖥️ | **OTTOU SIMON** |
| 🖥️ | **DOMCHE DANIELLE** |

> HTML5 · CSS3 · Bootstrap 5 · JavaScript ES6 · Chart.js · Templates Django

---

### 🔧 Responsabilités techniques

| Domaine | Responsable |
|---|---|
| 🌐 **Réseau** — Architecture LAN, IP fixes, routage, pare-feu | **ENGUENO RAFAEL** |
| 📊 **Monitoring** — Dashboard temps réel, psutil, graphiques | **OTTOU SIMON** |
| 🤖 **Intelligence Artificielle** — OpenAI, chatbot, anti-plagiat, correction | **PEH PEH SCOTT** |
| 🔒 **Sécurité** — Anti-brute force, journalisation, alertes, PowerShell | **ENGUENO RAFAEL** |

</div>

---

### 📬 Contact

Pour toute question relative au projet, contacter le chef de projet :
**DOMCHE DANIELLE** — KEYCE Informatique & IA, Yaoundé, Cameroun
