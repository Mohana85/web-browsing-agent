"""
Persistent task history repository in SQLite.
Records complete trajectory details, metrics, and outcomes for observability and post-task audit.
"""

import sqlite3
import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from agent.task_state import TaskState
from config import settings

logger = logging.getLogger("agent.memory.history")


class TaskHistoryRepository:
    """Stores full task trajectories in SQLite."""

    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or settings.sqlite_db_path
        self._init_db()

    def _init_db(self) -> None:
        """Initialize task history table schema."""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS task_history (
                    task_id TEXT PRIMARY KEY,
                    query TEXT NOT NULL,
                    task_type TEXT NOT NULL,
                    status TEXT NOT NULL,
                    final_answer TEXT,
                    visited_urls_json TEXT,
                    metrics_json TEXT,
                    created_at REAL,
                    updated_at REAL
                )
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_task_created ON task_history(created_at DESC)")
            conn.commit()

    def save_task(self, state: TaskState) -> None:
        """Persist or update task execution state."""
        visited_json = json.dumps(state.visited_urls)
        metrics_json = json.dumps(state.metrics.model_dump())

        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO task_history
                (task_id, query, task_type, status, final_answer, visited_urls_json, metrics_json, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                state.task_id,
                state.original_query,
                state.task_type.value,
                state.status.value,
                state.final_answer or "",
                visited_json,
                metrics_json,
                state.created_at,
                state.updated_at
            ))
            conn.commit()

    def list_recent_tasks(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Fetch list of recent tasks for UI rendering."""
        results = []
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("""
                SELECT task_id, query, task_type, status, final_answer, visited_urls_json, metrics_json, created_at
                FROM task_history
                ORDER BY created_at DESC
                LIMIT ?
            """, (limit,))
            for row in cursor.fetchall():
                item = dict(row)
                try:
                    item["visited_urls"] = json.loads(item["visited_urls_json"])
                    item["metrics"] = json.loads(item["metrics_json"])
                except Exception:
                    item["visited_urls"] = []
                    item["metrics"] = {}
                results.append(item)
        return results

    def clear_history(self) -> None:
        """Clear all stored task history."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM task_history")
            conn.commit()
