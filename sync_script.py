import datetime 
import os
import json
from dotenv import load_dotenv
from git import InvalidGitRepositoryError, Repo
from github import Github, GithubException


STATE_FILE="tracked_repos.json"
BACKDATE_COMMITS_TO_FOLDER_DATE = True
PARENT_DIRECTORIES = ["../Projects_test"]


# Load configuration from .env file
def load_config():
    load_dotenv()
    token = os.getenv("GITHUB_API_TOKEN")
    username = os.getenv("GITHUB_USERNAME")
    email = os.getenv("GITHUB_EMAIL")

    if not token or not username or not email:
        raise ValueError("Missing required environment variables.")
    return token, username, email


# Load tracking state from JSON file
def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r') as f:
            return json.load(f)
    return {}


# Save tracking state to JSON file
def save_state(state):
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=4)


# Get the commit date for a folder mtime or current date
def get_commit_date(folder_path):
    if BACKDATE_COMMITS_TO_FOLDER_DATE:
        timestamp = os.path.getmtime(folder_path)
        dt_object = datetime.datetime.fromtimestamp(timestamp)
        return dt_object
    
    return datetime.datetime.now()


# Check if there are uncommited changes in the repo
def has_uncommited_changes(repo):
    return repo.is_dirty(untracked_files=True)


# Create a GitHub repository or return existing one
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
        

# Ensure a .gitignore file exists in the folder
def ensure_gitignore(folder_path):
    gitignore_path = os.path.join(folder_path, ".gitignore") 

    if not os.path.exists(gitignore_path):
        with open(gitignore_path, 'w') as f:
            f.write("# Auto-generated .gitignore")
        return True
    else:
        print(f".gitignore already exists in {folder_path}.")
        return True
    

# Initialize local Git repository and set remote
def initialize_local_repo(folder_path, repo_url):
    try:
        repo = Repo(folder_path)
        print(f"Existing Git repository found in {folder_path}.")
    except InvalidGitRepositoryError:
        print(f"Initializing new Git repository in {folder_path}.")
        repo = Repo.init(folder_path)

    # if not ensure_gitignore(folder_path):
    #     return False
        
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

    repo.git.add(A=True)

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

        try:
            current_branch = repo.active_branch.name
        except TypeError:
            current_branch = 'main'
            print(f"couldn't determine current branch. Setting to {current_branch}.")
            repo.git.checkout('-B', current_branch)

        print("Pushing initial commit to remote repository.")
        origin.push(refspec=f"{current_branch}:{current_branch}", set_upstream=True)
    else:
        print(f"No changes to commit in {folder_path}.")

    print(f"Successfully configured local repo {folder_path} for {repo_url}.")
    return True


# Commit and push updates to remote repository
def push_updates(folder_path, commit_message):
    repo = Repo(folder_path)

    # Stage all changes
    repo.git.add(A=True)

    # Check if there are any changes to commit
    if not repo.is_dirty() and not repo.untracked_files:
        print(f"No changes to commit in {folder_path}.")
        return True
    
    # Get the commit date for the latest changes
    commit_date = get_commit_date(folder_path)

    # Create the commit
    if commit_date:
        repo.index.commit(
            commit_message,
            author_date=commit_date,
            commit_date=commit_date
        )
    else:
        repo.index.commit(commit_message)

    # get current branch name
    try:
        current_branch = repo.active_branch.name
    except TypeError:
        print(f"couldn't determine current branch. cannot push changes.")
        return False
    
    # Push the commit to the remote repository
    origin = repo.remote('origin')
    origin.push(refspec=f"{current_branch}:{current_branch}")
    print(f"Succesfully pushed changes to remote repository from {folder_path}.")
    return True


# def main():
#     token, username, email = load_config()
#     github_client = Github(token)
#     state = load_state()

#     potential_projects = {}

#     for parent_folder in PARENT_DIRECTORIES:

#         if not os.path.isdir(parent_folder):
#             print(f"Parent folder not found: {parent_folder}")
#             continue
        
#         print(f"Scanning inside: {parent_folder}")
        
#         try:
#             for item_name in os.listdir(parent_folder):
#                 item_path = os.path.join(parent_folder, item_name)
                
#                 if not os.path.isdir(item_path) or item_name.startswith('.'):
#                     print(f"Skipping non-directory or hidden item: {item_name}")
#                     continue
                
#                 # Check one level deeper for single subdirectory
#                 try:
#                     level1_contents = os.listdir(item_path)
#                     subdirs = [d for d in level1_contents
#                             if os.path.isdir(os.path.join(item_path, d)) and not d.startswith('.')]
                    
#                     if len(subdirs) == 1:
#                         sub_item_path = os.path.join(item_path, subdirs[0])
#                         print(f"Adding single sub-directory: {sub_item_path}")
                        
#                         if sub_item_path not in potential_projects:
#                             potential_projects[sub_item_path] = None
#                 except PermissionError:
#                     print(f"Permission denied accessing contents of {item_path}.")
#                 except Exception as e:
#                     print(f"Error checking contents of {item_path}: {e}")
        
#         except PermissionError:
#             print(f"Permission denied scanning directory {parent_folder}. Skipping.")
#         except Exception as e:
#             print(f"Error scanning directory {parent_folder}: {e}")
                        
                


    
