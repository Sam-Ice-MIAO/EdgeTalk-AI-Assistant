import os

from src.memory.sqlite_memory import SQLiteMemory
from src.memory.mysql_memory import MySQLMemory


def get_memory():
    backend = os.getenv("MEMORY_BACKEND", "sqlite").lower().strip()

    if backend == "mysql":
        return MySQLMemory()

    if backend == "sqlite":
        return SQLiteMemory()

    raise ValueError("MEMORY_BACKEND must be 'sqlite' or 'mysql'")
