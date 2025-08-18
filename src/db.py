import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from typing import Optional, Tuple
from config import DATABASE_PATH, DEFAULT_DAILY_QUOTA, DEFAULT_SOURCE_LANG, DEFAULT_TARGET_LANG


@contextmanager
def db() -> sqlite3.Connection:
    conn = sqlite3.connect(DATABASE_PATH)
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db() -> None:
    with db() as conn:
        source_default = DEFAULT_SOURCE_LANG.replace("'", "''")
        target_default = DEFAULT_TARGET_LANG.replace("'", "''")
        daily_quota_default = int(DEFAULT_DAILY_QUOTA)

        conn.execute(
            f"""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                source_lang TEXT NOT NULL DEFAULT '{source_default}',
                target_lang TEXT NOT NULL DEFAULT '{target_default}',
                daily_quota INTEGER NOT NULL DEFAULT {daily_quota_default},
                sent_today INTEGER NOT NULL DEFAULT 0,
                last_reset TEXT
            )
            """
        )


def ensure_user_row(user_id: int) -> None:
    with db() as conn:
        cur = conn.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,))
        if cur.fetchone() is None:
            conn.execute(
                "INSERT INTO users (user_id, source_lang, target_lang, daily_quota, sent_today, last_reset) VALUES (?, ?, ?, ?, 0, ?)",
                (user_id, DEFAULT_SOURCE_LANG, DEFAULT_TARGET_LANG, DEFAULT_DAILY_QUOTA, today_str()),
            )


def get_user_settings(user_id: int) -> Tuple[str, str, int, int, Optional[str]]:
    with db() as conn:
        cur = conn.execute(
            "SELECT source_lang, target_lang, daily_quota, sent_today, last_reset FROM users WHERE user_id = ?",
            (user_id,),
        )
        row = cur.fetchone()
        if row is None:
            ensure_user_row(user_id)
            return DEFAULT_SOURCE_LANG, DEFAULT_TARGET_LANG, DEFAULT_DAILY_QUOTA, 0, today_str()
        return row[0], row[1], int(row[2]), int(row[3]), row[4]


def update_user_lang(user_id: int, *, source: Optional[str] = None, target: Optional[str] = None) -> None:
    with db() as conn:
        if source and target:
            conn.execute(
                "UPDATE users SET source_lang = ?, target_lang = ? WHERE user_id = ?",
                (source, target, user_id),
            )
        elif source:
            conn.execute(
                "UPDATE users SET source_lang = ? WHERE user_id = ?",
                (source, user_id),
            )
        elif target:
            conn.execute(
                "UPDATE users SET target_lang = ? WHERE user_id = ?",
                (target, user_id),
            )


def update_user_quota(user_id: int, daily_quota: int) -> None:
    with db() as conn:
        conn.execute(
            "UPDATE users SET daily_quota = ? WHERE user_id = ?",
            (daily_quota, user_id),
        )


def today_str() -> str:
    return datetime.now(timezone.utc).date().isoformat()


def reset_usage_if_new_day(user_id: int) -> None:
    source, target, daily_quota, sent_today, last_reset = get_user_settings(user_id)
    if last_reset != today_str():
        with db() as conn:
            conn.execute(
                "UPDATE users SET sent_today = 0, last_reset = ? WHERE user_id = ?",
                (today_str(), user_id),
            )


def increment_usage(user_id: int) -> None:
    with db() as conn:
        conn.execute(
            "UPDATE users SET sent_today = sent_today + 1 WHERE user_id = ?",
            (user_id,),
        )


