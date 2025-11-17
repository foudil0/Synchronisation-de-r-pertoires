import datetime 
import os
import json
from dotenv import load_dotenv
from git import InvalidGitRepositoryError, Repo
from github import Github, GithubException


STATE_FILE="tracked_repos.json"
BACKDATE_COMMITS_TO_FOLDER_DATE = True


def load_config():
    load_dotenv()
    token = os.getenv("GITHUB_API_TOKEN")
    username = os.getenv("GITHUB_USERNAME")
    email = os.getenv("GITHUB_EMAIL")

    if not token or not username or not email:
        raise ValueError("Missing required environment variables.")
    return token, username, email


def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r') as f:
            return json.load(f)
    return {}


def save_state(state):
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=4)


def get_commit_date(folder_path):
    if BACKDATE_COMMITS_TO_FOLDER_DATE:
        timestamp = os.path.getmtime(folder_path)
        dt_object = datetime.datetime.fromtimestamp(timestamp)
        return dt_object
    
    return datetime.datetime.now()


def has_uncommited_changes(repo):
    return repo.is_dirty(untracked_files=True)


def create_github_repo(repo_name, is_private, description, github_client, username):
    try:
        user = github_client.get_user(username)
        repo = user.create_repo(
            name=repo_name,
            private=is_private,
            description=description or f"Project: {repo_name}",
            auto_init=False 
        )
        return repo.clone_url 
    except GithubException as e:
        if e.status == 422:
            print(f"Repository {repo_name} already exists on GitHub.")
            try:
                repo = user.get_repo(repo_name)
                print(f"Using existing repository {repo.html_url}.")
                return repo.clone_url
            except GithubException:
                print(f"Failed to access existing repository {repo_name}.")
                return None
        else:
            print(f"Failed to create repository {repo_name}: {e}")
            return None
        

def ensure_gitignore(folder_path):
    gitignore_path = os.path.join(folder_path, ".gitignore") 

    if not os.path.exists(gitignore_path):
        with open(gitignore_path, 'w') as f:
            f.write("# Auto-generated .gitignore")
        return True
    else:
        print(f".gitignore already exists in {folder_path}.")
        return True
    

def initialize_local_repo(folder_path, repo_url):
    try:
        repo = Repo(folder_path)
        print(f"Existing Git repository found in {folder_path}.")
    except InvalidGitRepositoryError:
        print(f"Initializing new Git repository in {folder_path}.")
        repo = Repo.init(folder_path)

        if not ensure_gitignore(folder_path):
            return False
        
        try:
            origin = repo.remote('origin') 
            current_url = next(origin.urls)

            if current_url == repo_url:
                print(f"Remote 'origin' already set to {repo_url}.")
            else:
                origin.set_url(repo_url)
                print(f"Updated remote 'origin' URL to {repo_url}.")
        except ValueError:
            origin = repo.create_remote('origin', repo_url)
            print(f"Set remote 'origin' to {repo_url}.")

        if repo.is_dirty() or repo.untracked_files:
            commit_date = get_commit_date(folder_path)

            if commit_date:
                repo.index.commit(
                    "Initial commit",
                    author=repo.config_reader().get_value("user", "name"),
                    author_email=repo.config_reader().get_value("user", "email"),
                    commit_date=commit_date.isoformat()
                )
            else:
                repo.index.commit("Initial commit")

            # a suivre 
            