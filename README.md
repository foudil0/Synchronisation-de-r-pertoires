# Synchronisation de Répertoires - L3 Projet

Synchronisation automatique de répertoires locaux vers des dépôts GitHub privés avec gestion des conflits et surveillance en temps réel.

## 👥 Équipe

| Nom | Prénom | Rôle |
|-----|--------|------|
| IDIR | Salah | Surveillance et synchronisation (`watch_and_sync.py`), Gestion des conflits |
| HOCINI | Foudil | Configuration, État, Opérations Git de base |

## 📋 Structure du Projet

```
.
├── sync_script.py              # Script principal de synchronisation Git
├── watch_and_sync.py           # Surveillance des changements en temps réel
├── tracked_repos.json          # État des projets synchronisés
├── group.csv                   # Informations du groupe
├── .env                        # Variables d'environnement (token GitHub)
├── .gitignore                  # Fichiers à ignorer
└── README.md                   
```

## 📦 Dépendances

Le projet utilise les bibliothèques Python suivantes :

| Bibliothèque | Utilisation |
|--------------|-----------|
| `GitPython` | Opérations Git (commit, push, pull) |
| `PyGithub` | Création et gestion des dépôts GitHub |
| `python-dotenv` | Chargement des variables d'environnement |
| `watchdog` | Surveillance des changements de fichiers en temps réel |

### Installation des dépendances

```bash
pip install GitPython PyGithub python-dotenv watchdog
```

## 🚀 Configuration et Démarrage

### 1. Configuration des variables d'environnement

Créez un fichier `.env` à la racine du projet :

```env
GITHUB_API_TOKEN=votre_token_github
GITHUB_USERNAME=votre_nom_utilisateur
GITHUB_EMAIL=votre_email@example.com
```


### 2. Structure des répertoires

Créez les répertoires parents à surveiller :

```bash
mkdir -p ../Projects_test
```

Placez vos projets dans ce répertoire :

```
../Projects_test/
├── Projet1/
├── Projet2/
└── Projet3/
```

### 3. Exécution

#### Mode de surveillance en temps réel 

```bash
python watch_and_sync.py
```

Le script va :
- Surveiller les changements dans `../Projects_test/`
- Détecter automatiquement les nouveaux projets
- Synchroniser les modifications en temps réel avec un délai de 5 secondes

#### Mode de synchronisation unique

```bash
python sync_script.py
```

Synchronise tous les projets une seule fois.


## 🔧 Fonctionnalités Principales

### `sync_script.py`

**Configuration & État :**
- `load_config()` - Charge les variables d'environnement
- `load_state()` / `save_state()` - Gère l'état des projets synchronisés dans `tracked_repos.json`

**Opérations Git :**
- `initialize_local_repo()` - Initialise un dépôt Git local
- `push_updates()` - Pousse les modifications vers GitHub
- `pull_updates()` - Récupère les changements distants
- `has_uncommited_changes()` - Détecte les changements non committés

**Gestion GitHub :**
- `create_github_repo()` - Crée ou récupère un dépôt GitHub privé
- `ensure_gitignore()` - Crée un `.gitignore` si absent

**Gestion des Conflits :**
- `handle_conflict_rename_local()` - Résout les conflits de fusion :
  - Sauvegarde la version locale avec un timestamp
  - Accepte la version distante
  - Crée un merge commit automatique

### `watch_and_sync.py`

**Surveillance :**
- `ChangeHandler` - Détecte les modifications de fichiers
- `on_modified()` / `on_created()` / `on_deleted()` - Événements de fichiers
- `schedule_sync()` - Planifie la synchronisation avec délai de 5 secondes

**Nouveaux Projets :**
- Détection automatique des nouveaux répertoires
- Création de dépôts GitHub automatiquement
- Synchronisation initiale complète

**Filtrage :**
- Ignore les fichiers : `.git`, `__pycache__`, `.env`, `node_modules`, etc.

## 📊 Fichier État (`tracked_repos.json`)

Format du fichier de suivi :

```json
{
    "/path/to/project": {
        "repo_name": "project-name",
        "repo_url": "https://token@github.com/username/project-name.git",
        "last_sync": "2024-01-15T10:30:00+00:00"
    }
}
```

## ⚙️ Configuration Personnalisable

### Dans `watch_and_sync.py`

```python
SYNC_DELAY = 5  # Délai avant synchronisation (secondes)
PARENTS_DIR = ["../Projects_test"]  # Répertoires à surveiller
```

### Dans `sync_script.py`

```python
PARENT_DIRECTORIES = ["../Projects_test"]  # Répertoires à scanner
BACKDATE_COMMITS_TO_FOLDER_DATE = False  # Antidater les commits
```

## 🛡️ Gestion des Conflits

Quand un conflit de fusion est détecté :

1. La version locale est sauvegardée avec un timestamp
2. La version distante est acceptée
3. Les deux fichiers sont committés
4. Un merge commit est créé automatiquement

**Exemple :**
```
fichier.txt → conflit détecté
fichier_local_20240115_103000.txt → sauvegarde locale
fichier.txt → contient la version distante
```

## 📝 Fichiers Ignorés

Les fichiers suivants ne déclenchent pas de synchronisation :

```
.git, __pycache__, .pyc, .venv, venv, .env,
node_modules, .DS_Store, tracked_repos.json, _local_
```

## 📚 Exemples d'Utilisation

### Ajouter un nouveau projet

```bash
# 1. Créer le répertoire
mkdir ../Projects_test/MonProjet

# 2. Le script va :
#    - Détecter le nouveau répertoire
#    - Créer un dépôt GitHub automatiquement
#    - Initialiser le repo Git local
#    - Pousser les fichiers initiaux
```

### Modifier un projet existant

```bash
# Les modifications sont détectées et synchronisées automatiquement
# en temps réel (délai de 5 secondes)
```

