import os
import pymysql
from datetime import datetime


class MySQLMemory:
    def __init__(self):
        self.host = os.getenv("MYSQL_HOST", "127.0.0.1")
        self.port = int(os.getenv("MYSQL_PORT", "3306"))
        self.user = os.getenv("MYSQL_USER", "root")
        self.password = os.getenv("MYSQL_PASSWORD", "edgetalk123")
        self.database = os.getenv("MYSQL_DATABASE", "edgetalk")

        self.init_db()

    def get_connection(self):
        return pymysql.connect(
            host=self.host,
            port=self.port,
            user=self.user,
            password=self.password,
            database=self.database,
            charset="utf8mb4",
            cursorclass=pymysql.cursors.DictCursor,
        )

    def init_db(self):
        sql = """
        CREATE TABLE IF NOT EXISTS messages (
            id INT AUTO_INCREMENT PRIMARY KEY,
            session_id VARCHAR(128) NOT NULL,
            role VARCHAR(32) NOT NULL,
            content TEXT NOT NULL,
            created_at DATETIME NOT NULL,
            INDEX idx_session_id (session_id),
            INDEX idx_created_at (created_at)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """

        conn = self.get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(sql)
            conn.commit()
        finally:
            conn.close()

    def save_message(self, session_id: str, role: str, content: str):
        sql = """
        INSERT INTO messages (session_id, role, content, created_at)
        VALUES (%s, %s, %s, %s)
        """

        conn = self.get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    sql,
                    (
                        session_id,
                        role,
                        content,
                        datetime.now(),
                    ),
                )
            conn.commit()
        finally:
            conn.close()

    def get_recent_messages(self, session_id: str, limit: int = 10):
        sql = """
        SELECT session_id, role, content, created_at
        FROM messages
        WHERE session_id = %s
        ORDER BY created_at DESC, id DESC
        LIMIT %s
        """

        conn = self.get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(sql, (session_id, limit))
                rows = cursor.fetchall()
        finally:
            conn.close()

        rows = list(reversed(rows))

        for row in rows:
            row["created_at"] = str(row["created_at"])

        return rows
