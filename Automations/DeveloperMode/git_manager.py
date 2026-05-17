import subprocess


def init_git(root):

    subprocess.call(["git", "init"], cwd=root)
    subprocess.call(["git", "add", "."], cwd=root)
    subprocess.call(["git", "commit", "-m", "Initial AI commit"], cwd=root)
