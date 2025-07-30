import subprocess

def get_git_commit_message():
    try:
        result = subprocess.check_output(["git", "log", "-1", "--pretty=%s"])
        return result.decode("utf-8").strip()
    except Exception:
        return "не удалось получить версию"