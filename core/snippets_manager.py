# core/snippets_manager.py

import json
import uuid
from datetime import datetime
from pathlib import Path


class SnippetsManager:
    def __init__(self, filepath="data/snippets.json"):
        self.filepath = Path(filepath)
        self.snippets = []
        self._ensure_file()
        self.load()

    # ---------- FILE HANDLING ----------

    def _ensure_file(self):
        """Crea el archivo si no existe"""
        if not self.filepath.exists():
            self.filepath.parent.mkdir(parents=True, exist_ok=True)
            with open(self.filepath, "w", encoding="utf-8") as f:
                json.dump([], f, indent=4, ensure_ascii=False)

    def load(self):
        with open(self.filepath, "r", encoding="utf-8") as f:
            self.snippets = json.load(f)

    def save(self):
        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump(self.snippets, f, indent=4, ensure_ascii=False)

    # ---------- VALIDATION ----------

    def _validate(self, data):
        required_fields = ["group", "title", "content"]

        for field in required_fields:
            if not data.get(field):
                raise ValueError(f"El campo '{field}' es obligatorio.")

    # ---------- CRUD ----------

    def get_all(self):
        return self.snippets

    def get_by_id(self, snippet_id):
        for s in self.snippets:
            if s["id"] == snippet_id:
                return s
        return None

    def add(self, group, title, content, tags=None):
        data = {
            "group": group,
            "title": title,
            "content": content
        }

        self._validate(data)

        now = datetime.now().isoformat()

        snippet = {
            "id": str(uuid.uuid4()),
            "group": group,
            "title": title,
            "content": content,
            "tags": tags or [],
            "created_at": now,
            "updated_at": now
        }

        self.snippets.append(snippet)
        self.save()
        return snippet

    def update(self, snippet_id, **kwargs):
        snippet = self.get_by_id(snippet_id)
        if not snippet:
            raise ValueError("Snippet no encontrado.")

        # actualizar campos permitidos
        for field in ["group", "title", "content", "tags"]:
            if field in kwargs:
                snippet[field] = kwargs[field]

        # validar después de cambios
        self._validate(snippet)

        snippet["updated_at"] = datetime.now().isoformat()
        self.save()
        return snippet

    def delete(self, snippet_id):
        original_len = len(self.snippets)
        self.snippets = [s for s in self.snippets if s["id"] != snippet_id]

        if len(self.snippets) == original_len:
            raise ValueError("Snippet no encontrado.")

        self.save()

    # ---------- SEARCH / FILTER ----------

    def search(self, text):
        text = text.lower()
        return [
            s for s in self.snippets
            if text in s["title"].lower() or text in s["content"].lower()
        ]

    def filter_by_group(self, group):
        return [s for s in self.snippets if s["group"] == group]