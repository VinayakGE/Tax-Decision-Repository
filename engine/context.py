"""EvidenceContext — the shared state dict passed through every rule execution."""


class EvidenceContext:
    def __init__(self, initial: dict = None):
        self._data = dict(initial or {})

    def has(self, key: str) -> bool:
        return key in self._data

    def has_all(self, keys) -> bool:
        return all(self.has(k) for k in keys)

    def get(self, key: str, default=None):
        return self._data.get(key, default)

    def set(self, key: str, value) -> None:
        self._data[key] = value

    def update(self, mapping: dict) -> None:
        self._data.update(mapping)

    def snapshot(self) -> dict:
        return dict(self._data)
