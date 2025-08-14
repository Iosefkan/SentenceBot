from telegram import Update
from telegram.ext import Application, ApplicationBuilder, CommandHandler

from config import BOT_TOKEN
from db import init_db
from handlers import (
    cmd_get,
    cmd_help,
    cmd_languages,
    cmd_set_quota,
    cmd_set_source,
    cmd_set_target,
    cmd_start,
)


def build_app() -> Application:
    init_db()
    app: Application = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("help", cmd_help))
    app.add_handler(CommandHandler("languages", cmd_languages))
    app.add_handler(CommandHandler("get", cmd_get))
    app.add_handler(CommandHandler("set_source", cmd_set_source))
    app.add_handler(CommandHandler("set_target", cmd_set_target))
    app.add_handler(CommandHandler("set_quota", cmd_set_quota))
    return app


def main() -> None:
    app = build_app()
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()


