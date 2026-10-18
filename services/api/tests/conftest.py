"""Test isolation: throwaway SQLite DB, no token auth, before any app import."""

import os

os.environ["DATABASE_URL"] = "sqlite+aiosqlite:////tmp/novapilot-test.db"
os.environ["NOVAPILOT_TOKEN"] = ""
os.environ["MODEL_DEFAULT"] = "test/echo"

_db = "/tmp/novapilot-test.db"
if os.path.exists(_db):
    os.remove(_db)
