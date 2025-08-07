import re
from locator_repair.config import LOCATOR_FILE_PATH, REPO_PATH, BRANCH_NAME
from git import GitCommandError, Repo

def update_locator_by_variable(locator_file_path, locator_name, new_locator):
    """
    Updates the given locator variable in the locator file with the new locator.

    Args:
        locator_file_path (str): Path to the Python locator file.
        locator_name (str): Variable name of the locator (e.g., 'EMAILBOX_LOCATOR').
        new_locator (tuple): New locator tuple, e.g., ('xpath', '//input[@id="email"]')
    """

    strategy, selector = new_locator
    strategy = strategy.upper()  # Convert 'xpath' to 'XPATH'

    updated_line = f"{locator_name} = (By.{strategy}, \"{selector}\")\n"

    pattern = re.compile(rf"^{locator_name}\s*=\s*\(By\.\w+,\s*['\"].*?['\"]\)")

    updated = False
    with open(locator_file_path, 'r') as file:
        lines = file.readlines()

    with open(locator_file_path, 'w') as file:
        for line in lines:
            if pattern.match(line):
                file.write(updated_line)
                print(f"🔁 Updated: {locator_name} → {updated_line.strip()}")
                updated = True
            else:
                file.write(line)

    if not updated:
        print(f"⚠️ Locator variable '{locator_name}' not found in {locator_file_path}")

def commit_and_push_changes():
    repo = Repo(REPO_PATH)

    current_branch = repo.active_branch.name
    print(f"🌿 Current branch: {current_branch}")

    # Step 1: Create new branch from current working branch (e.g., ai-locator)
    try:
        repo.git.checkout('-b', BRANCH_NAME)
    except GitCommandError:
        print(f"⚠️ Branch '{BRANCH_NAME}' already exists. Checking it out.")
        repo.git.checkout(BRANCH_NAME)

    # Step 2: Pull latest main and merge into this new branch
    repo.git.fetch('origin', 'main')  # fetch updates from remote
    repo.git.merge('origin/main')     # merge into the current (new) branch
    print("🔄 Merged latest changes from origin/main")

    # Step 3: Stage and commit any local changes
    if repo.is_dirty(untracked_files=True):
        repo.git.add(A=True)
        repo.index.commit(f"AI Fix: Broken locator committed to {BRANCH_NAME}")
        print("✅ Local changes committed.")
    else:
        print("⚠️ No local changes to commit.")

    # Step 4: Push new branch to origin
    repo.git.push('--set-upstream', 'origin', BRANCH_NAME)
    print(f"🚀 Changes pushed to branch '{BRANCH_NAME}'")

