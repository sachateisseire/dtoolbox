from PySide6.QtCore import QObject, Signal


class SnippetsService(QObject):

    data_changed = Signal()  # 🔥 señal

    def __init__(self, manager):
        super().__init__()
        self.manager = manager

    # ---------- GET ----------

    def get_all(self):
        return self.manager.get_all()

    def get_by_id(self, snippet_id):
        return self.manager.get_by_id(snippet_id)

    # ---------- CRUD ----------

    def add(self, group, title, content, tags=None):
        if not title or not title.strip():
            raise ValueError("El título no puede estar vacío")

        result = self.manager.add(group, title, content, tags)
        self.data_changed.emit()  # 🔥 avisar
        return result

    def update(self, snippet_id, **kwargs):
        result = self.manager.update(snippet_id, **kwargs)
        self.data_changed.emit()
        return result

    def delete(self, snippet_id):
        result = self.manager.delete(snippet_id)
        self.data_changed.emit()
        return result

    # ---------- SEARCH ----------

    def search(self, text):
        return self.manager.search(text)

    def filter_by_group(self, group):
        return self.manager.filter_by_group(group)