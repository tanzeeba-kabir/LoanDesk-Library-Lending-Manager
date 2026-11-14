"""The Holdings model: copies owned and copies borrowed per title."""
from loandesk.storage import load_json, save_json


class Holdings:
    """Tracks copies owned and borrowed for each title.

    Data shape, the same as holdings.json:
        {"Hamlet": {"copies": 5, "borrowed": 3}, ...} these are dictionaries

    On the shelf = copies - borrowed.
    """

    def __init__(self, data=None):
        """Store the holdings dictionary, or start empty if none is given."""
        # self._data is this object's memory: the dict of all titles.
        self._data = data if data is not None else {}

    def _find_key(self, title):
        """Return the stored spelling of `title` (ignoring case), or None."""
        for stored_title in self._data:
            if stored_title.lower() == title.strip().lower():
                return stored_title
        return None

    def shelf(self, title):
        """Return copies on the shelf (0 if the title is unknown)."""
        key = self._find_key(title)
        if key is None:
            return 0
        return self._data[key]["copies"] - self._data[key]["borrowed"]

    def add(self, title, quantity):
        """Acquire copies: increase `copies` only.

        A new title is created with borrowed set to 0.
        Raises ValueError if quantity is zero or negative.
        """
        if quantity <= 0:
            raise ValueError("Quantity must be a positive integer.")

        key = self._find_key(title)
        if key is None:
            self._data[title.strip()] = {
                "copies": quantity,
                "borrowed": 0,
            }
        else:
            self._data[key]["copies"] += quantity

    def return_copies(self, title, quantity):
        """Copies come back: decrease `borrowed` only.

        Raises ValueError if quantity is not positive, or if it is more than
        the number currently borrowed (an unknown title counts as 0 borrowed).
        The holdings are left unchanged when an error is raised.
        """
        if quantity <= 0:
            raise ValueError("Quantity must be a positive integer.")

        key = self._find_key(title)
        if key is None:
            borrowed = 0
        else:
            borrowed = self._data[key]["borrowed"]

        if quantity > borrowed:
            raise ValueError(
                f"Cannot RETURN {quantity} of '{title}',"
                f"only {borrowed} borrowed."
            )
        self._data[key]["borrowed"] -= quantity

    def shortfalls(self, needs):
        """Return {title: missing} for every title that is short.

        missing = need - shelf. Titles that are fully covered are left out.
        """
        missing = {}
        for title, need in needs.items():
            shelf = self.shelf(title)
            if need > shelf:
                missing[title] = need - shelf
        return missing

    def can_lend(self, needs):
        """Return True if every needed title has enough copies on the shelf."""
        return not self.shortfalls(needs)

    def lend(self, needs):
        """Lend a whole request: increase `borrowed` only, all or nothing.

        Raises ValueError, changing nothing, if any title is short.
        """
        missing = self.shortfalls(needs)
        if missing:
            raise ValueError(f"Not enough copies on the shelf: {missing}")

        for title, quantity in needs.items():
            key = self._find_key(title)
            if key is not None:
                self._data[key]["borrowed"] += quantity

    @classmethod
    def load(cls, filepath):
        """Load holdings data from a JSON file and create a Holdings object."""
        return cls(load_json(filepath))

    def save(self, filepath):
        """Write the holdings to a JSON file."""
        save_json(filepath, self._data)
