"""
wine_repository.py
------------------
SOLID principles applied:
  S — Single responsibility: all SQLite wine data access lives here.
      Nothing else knows how wines are stored.

Security fix: uses parameterised queries (?) instead of f-string interpolation
to prevent SQL injection.
"""

import sqlite3


class WineRepository:
    """Data access object for the wine SQLite database."""

    def __init__(self, db_path: str = "wine_database.db"):
        self._db_path = db_path
        # Lazy cache — populated on first call to get_all_wine_names()
        self._cached_names: list = []

    def get_all_wine_names(self) -> list:
        """Return all wine names; result is cached for the lifetime of this instance."""
        if not self._cached_names:
            with sqlite3.connect(self._db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT wine FROM wine_links")
                self._cached_names = [row[0] for row in cursor.fetchall()]
        return self._cached_names

    def get_wine_url(self, wine_name: str) -> str:
        """Return the purchase URL for a wine, or a search-fallback URL."""
        with sqlite3.connect(self._db_path) as conn:
            cursor = conn.cursor()
            # Parameterised query prevents SQL injection
            cursor.execute("SELECT link FROM wine_links WHERE wine = ?", (wine_name,))
            result = cursor.fetchone()
        if result:
            return result[0]
        return f"https://www.wine.com/product/search?query={wine_name.replace(' ', '+')}"
