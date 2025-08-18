from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from config import DEFAULT_DAILY_QUOTA, SUPPORTED_LANGUAGES, logger
from db import (
    ensure_user_row,
    get_user_settings,
    increment_usage,
    reset_usage_if_new_day,
    update_user_lang,
    update_user_quota,
)
from language import normalize_lang_code, translate
from sentence import generate_base_sentence
from tts import synthesize_to_wav


def parse_arg_after_command(update: Update) -> str | None:
    if update.message is None or update.message.text is None:
        return None
    parts = update.message.text.split(maxsplit=1)
    return parts[1].strip() if len(parts) > 1 else None


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    assert update.effective_user is not None
    user_id = update.effective_user.id
    ensure_user_row(user_id)
    source, target, daily_quota, sent_today, _ = get_user_settings(user_id)

    text_lines = [
        "Welcome! I send sentences in your target language with audio and a translation.",
        "",
        f"Current settings:",
        f"- Source language: {SUPPORTED_LANGUAGES[source]['name']} ({source})",
        f"- Target language: {SUPPORTED_LANGUAGES[target]['name']} ({target})",
        f"- Daily quota: {daily_quota} (used today: {sent_today})",
        "",
        "Commands:",
        "- /get — receive one sentence now (respects daily quota)",
        "- /set_source <code> — set your source language",
        "- /set_target <code> — set your target language",
        "- /set_quota <n> — set your daily sentence limit",
        "- /languages — list supported language codes",
        "- /help — show help",
    ]
    await update.message.reply_text("\n".join(text_lines))


async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await cmd_start(update, context)


async def cmd_set_source(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    assert update.effective_user is not None
    user_id = update.effective_user.id
    ensure_user_row(user_id)
    arg = parse_arg_after_command(update)
    if not arg:
        await update.message.reply_text("Usage: /set_source <language_code>. Try /languages for supported codes.")
        return
    code = normalize_lang_code(arg)
    if not code:
        await update.message.reply_text("Unsupported language code. Try /languages.")
        return
    update_user_lang(user_id, source=code)
    await update.message.reply_text(f"Source language set to {SUPPORTED_LANGUAGES[code]['name']} ({code}).")


async def cmd_set_target(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    assert update.effective_user is not None
    user_id = update.effective_user.id
    ensure_user_row(user_id)
    arg = parse_arg_after_command(update)
    if not arg:
        await update.message.reply_text("Usage: /set_target <language_code>. Try /languages for supported codes.")
        return
    code = normalize_lang_code(arg)
    if not code:
        await update.message.reply_text("Unsupported language code. Try /languages.")
        return
    update_user_lang(user_id, target=code)
    await update.message.reply_text(f"Target language set to {SUPPORTED_LANGUAGES[code]['name']} ({code}).")


async def cmd_set_quota(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    assert update.effective_user is not None
    user_id = update.effective_user.id
    ensure_user_row(user_id)
    arg = parse_arg_after_command(update)
    if not arg:
        await update.message.reply_text("Usage: /set_quota <number>")
        return
    try:
        n = int(arg)
        if n < 1 or n > 100:
            await update.message.reply_text("Please choose a number between 1 and 100.")
            return
    except ValueError:
        await update.message.reply_text("Invalid number. Usage: /set_quota <number>")
        return
    update_user_quota(user_id, n)
    await update.message.reply_text(f"Daily quota set to {n}.")


async def cmd_languages(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    lines = ["Supported languages (code — name):"]
    for code, meta in sorted(SUPPORTED_LANGUAGES.items()):
        lines.append(f"{code} — {meta['name']}")
    await update.message.reply_text("\n".join(lines))


async def cmd_get(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    assert update.effective_user is not None
    user_id = update.effective_user.id
    ensure_user_row(user_id)
    reset_usage_if_new_day(user_id)
    source, target, daily_quota, sent_today, _ = get_user_settings(user_id)
    if sent_today >= daily_quota:
        await update.message.reply_text(
            f"Daily quota reached ({sent_today}/{daily_quota}). Try again tomorrow or increase with /set_quota."
        )
        return

    try:
        base = generate_base_sentence(SUPPORTED_LANGUAGES[source]['name'])
    except Exception as e:
        logger.error(e)
        await update.message.reply_text("Sorry, sentence generation failed. Please try again.")
        return
    
    try:
        target_sentence = translate(base, target)
    except Exception as e:
        logger.error(e)
        await update.message.reply_text("Sorry, translation failed. Please try again.")
        return

    try:
        wav_path = synthesize_to_wav(target_sentence, target)
    except Exception as e:
        logger.error(e)
        await update.message.reply_text("Sorry, TTS synthesis failed. Please try again.")
        return

    try:
        caption = (
            f"Original in {SUPPORTED_LANGUAGES[source]['name']}:\n"
            f"<b>{base}</b>\n-------------------------------------------\n"
            f"Translation to {SUPPORTED_LANGUAGES[target]['name']}:\n"
            f"<b>{target_sentence}</b>"
        )
        assert update.message is not None
        with open(wav_path, "rb") as f:
            await update.message.reply_document(document=f, caption=caption, parse_mode=ParseMode.HTML, filename="audio.mp3")
        increment_usage(user_id)
    finally:
        try:
            import os
            os.remove(wav_path)
        except Exception:
            pass


