# Synchronisation de répertoires

## Objectif du projet

Développer un outil permettant la **synchronisation automatique de répertoires entre plusieurs machines** en utilisant un **serveur Git** pour centraliser les fichiers.

L'application côté client doit :
- surveiller les fichiers locaux ;
- créer automatiquement des commits en cas de modification ;
- synchroniser les changements avec le serveur (push/pull) ;
- gérer les conflits éventuels.

---

## Répartition des tâches

| Étudiant | Partie du projet | Fichiers concernés | Librairies utilisées |
|----------|------------------|---------------------|----------------------|
| **Hocini Foudil** | **"Setup & One-time Sync" System** | `sync_script.py`, `test_script.py` | `datetime`, `os`, `json`, `python-dotenv`, `GitPython`, `PyGithub` |
| **Salah Idir** | **"Real-time Watcher" System** | `watcher_script.py` | `watchdog`, `threading`, `time`, `datetime`, `traceback` |

---

## Noyau minimal 

Fonctionnalités indispensables pour obtenir une version fonctionnelle de base.

| Fonctionnalité | Description | Python standard | Bib tierce | Outils indépendants |
|----------------|-------------|-----------------|------------|----------------------|
| Surveillance des fichiers locaux | Détecter toute modification (création, suppression, modification) dans un répertoire. | `os`, `pathlib`, `time` | `watchdog` | `inotifywait` |
| Création automatique de commits | Enregistrer les changements détectés sous forme de commits locaux. | `subprocess` (commandes git) | `GitPython` | `pygit2` |
| Push vers le serveur Git | Envoyer les commits locaux sur le serveur central. | `subprocess` (commandes git) | `GitPython` | `pygit2` |
| Pull depuis le serveur Git | Récupérer les mises à jour effectuées sur le serveur. | `subprocess` (commandes git) | `GitPython` | `pygit2` |
| Gestion des conflits | Détecter les conflits et créer une duplication des fichiers concernés. | | `GitPython` | |

---

## Fonctionnalités complémentaires

Fonctionnalités qui viennent enrichir le noyau minimal sans être indispensables au fonctionnement de base.

| Fonctionnalité | Description | Python standard | Bib tierce | Outils indépendants |
|----------------|-------------|-----------------|------------|----------------------|
| Interface de configuration | Choisir le répertoire à surveiller et la fréquence de synchronisation. | `json` | `PyMAL`, `tkinter`, `PyQt6` | |
| Journal d'activité | Enregistrer les actions (commits, push, pull, conflits). | `logging` | `loguru` | |
| Notifications utilisateur | Prévenir l'utilisateur en cas de conflit ou d'erreur. | | `plyer`, `win10toast` | `notify-send` (Linux) |

---

## Librairies utilisées dans notre projet

### **Partie 1: "Setup & One-time Sync" System** (Hocini Foudil)

| Librairie | Service rendu | Installation | Utilisation |
|-----------|---------------|--------------|-------------|
| **`datetime`** | Gestion des dates/heures pour les commits | Python standard | Simple |
| **`os`** | Parcourir répertoires, lire fichiers, vérifier dates | Python standard | Simple |
| **`json`** | Sauvegarde/chargement état de synchronisation | Python standard | Simple |
| **`python-dotenv`** | Chargement variables d'environnement | `pip install python-dotenv` | Simple |
| **`GitPython`** | API Git: `repo.is_dirty()`, `repo.git.add()`, `repo.index.commit()` | `pip install GitPython` | Simple, automatisation Git |
| **`PyGithub`** | Interaction avec GitHub API (création repos, gestion) | `pip install PyGithub` | Simple, gestion GitHub |

**Limites:**
- GitPython: Lent sur gros dépôts
- PyGithub: Nécessite token GitHub

### **Partie 2: "Real-time Watcher" System** (À déterminer)

| Librairie | Service rendu | Installation | Utilisation |
|-----------|---------------|--------------|-------------|
| **`watchdog`** | Surveillance temps réel des événements système | `pip install watchdog` | Simple, événementiel |
| **`threading`** | Gestion timers et opérations asynchrones | Python standard | Complexe (concurrence) |
| **`time`** | Gestion délais et débouncing | Python standard | Simple |
| **`datetime`** | Horodatage événements | Python standard | Simple |
| **`traceback`** | Debugging et gestion erreurs | Python standard | Simple |

**Limites:**
- Watchdog: Dépend librairies natives (inotify sur Linux)
- Threading: Gestion concurrence complexe

---

## Librairies évaluées mais non retenues

| Librairie | Raison du non-choix |
|-----------|----------------------|
| **`inotifywait`** | Linux seulement, pas portable |
| **`subprocess` + git** | Très fragile, gestion manuelle erreurs |
| **`pygit2`** | Installation complexe, documentation limitée |
| **`PyMAL`/`tkinter`/`PyQt6`** | Interface graphique non prioritaire |
| **`loguru`** | `logging` standard suffisant |

---

## Choix techniques justifiés

### Pour la partie 1 (Setup & Sync):
- **GitPython**: Meilleur équilibre simplicité/fonctionnalités
- **PyGithub**: API officielle GitHub, bien documentée
- **python-dotenv**: Sécurisation credentials

### Pour la partie 2 (Watcher):
- **watchdog**: Surveillance temps réel multiplateforme
- **threading**: Nécessaire pour débouncing et non-blocage

### Commun aux deux parties:
- **JSON**: Format simple pour état de synchronisation
  
