"""The Request model: one reading-list request."""

from loandesk.storage import load_json


class Request:
    """A reading-list request: a name and the books it needs."""

    def __init__(self, name, books):
        """Store the request name and the needed books."""
        self.name = name
        self.books = books

    def matches(self, name):
        """Return True if `name` matches this request (ignoring case)."""
        return self.name.strip().lower() == name.strip().lower()

    @classmethod
    def load_all(cls, filepath):
        """Read the requests file and return a list of Request objects."""
        items = load_json(filepath)
        return [cls(item["name"], item["books"]) for item in items]
