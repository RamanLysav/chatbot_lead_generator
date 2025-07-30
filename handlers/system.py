import subprocess
from telegram import Update
from telegram.ext import ContextTypes

def get_git_commit_message():
    try:
        msg = subprocess.check_output(["git", "log", "-1", "--pretty=%s"])
        return msg.decode("utf-8").strip()
    except Exception:
        return "не удалось получить версию"

async def about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    commit = get_git_commit_message()
    await update.message.reply_text(f"🤖 Версия бота: `{commit}`", parse_mode="Markdown")