"""Test isolation: throwaway SQLite DB, no token auth, before any app import."""

import os

os.environ["DATABASE_URL"] = "sqlite+aiosqlite:////tmp/actlet-test.db"
os.environ["ACTLET_TOKEN"] = ""
os.environ["MODEL_DEFAULT"] = "test/echo"

_db = "/tmp/actlet-test.db"
if os.path.exists(_db):
    os.remove(_db)
