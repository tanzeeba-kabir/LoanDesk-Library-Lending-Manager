"""LoanDeskManager: the controller that runs every command."""

import os
import shlex


class LoanDeskManager:
    """Connects the requests and the holdings to the user's commands."""

    def __init__(self, holdings, requests, holdings_path, report_path):
        """Store the models and the file paths from config.json."""
        self.holdings = holdings
        self.requests = requests
        self.holdings_path = holdings_path
        self.report_path = report_path

 

    def save_holdings(self):
        """Write the current holdings to the holdings file."""
        self.holdings.save(self.holdings_path)

    def find_request(self, name):
        """Return the request called `name` (ignoring case), or None."""
        for request in self.requests:
            if request.matches(name):
                return request
        return None

    def require_request(self, name):
        """Return the request, or raise ValueError if not found."""
        request = self.find_request(name)
        if request is None:
            raise ValueError(f"Request '{name}' not found.")
        return request

    def list_requests(self):
        """Return the request names in file order."""
        return [request.name for request in self.requests]

    def request_gap(self, name):
        """Return {title: missing} for the named request."""
        request = self.require_request(name)
        return self.holdings.shortfalls(request.books)

    def lend_request(self, name):
        """Lend the named request (all or nothing)."""
        request = self.require_request(name)
        self.holdings.lend(request.books)

    def plan(self):
        """Return the names of every request the desk can lend right now."""
        return [
            request.name
            for request in self.requests
            if self.holdings.can_lend(request.books)
        ]

    def add_book(self, title, quantity):
        """Add copies of a title."""
        self.holdings.add(title, quantity)

    def return_book(self, title, quantity):
        """Return borrowed copies of a title."""
        self.holdings.return_copies(title, quantity)

    @staticmethod
    def parse_quantity(text):
        """Turn text into a positive int, or raise ValueError."""
        try:
            quantity = int(text)
        except ValueError:
            raise ValueError(f"Quantity must be a whole number, got '{text}'.")
        if quantity <= 0:
            raise ValueError("Quantity must be a positive integer.")
        return quantity

    # command routing

    def execute(self, tokens):
        """Run one command given as a list of words, never crashing."""
        try:
            self._dispatch(tokens)
        except ValueError as error:
            print(f"Error: {error}")
        except OSError as error:
            print(f"File error: {error}")

    def _dispatch(self, tokens):
        """Send the command to the right handler."""
        if not tokens:
            raise ValueError("No command entered.")

        command = tokens[0].lower()
        args = tokens[1:]

        if command == "plan" and not args:
            self._print_plan()
        elif command == "request":
            self._request_command(args)
        elif command == "books":
            self._books_command(args)
        else:
            raise ValueError(f"Unknown command '{tokens[0]}'.")

    def _print_plan(self):
        """Print the requests that can be lent now."""
        results = self.plan()
        if not results:
            print("No request can be lent with the current shelves.")
            return
        print("Requests the desk can lend:")
        for name in results:
            print(f"- {name}")

    def _request_command(self, args):
        """Handle request list / view / gap / lend."""
        sub = args[0].lower() if args else ""

        if sub == "list" and len(args) == 1:
            for number, name in enumerate(self.list_requests(), start=1):
                print(f"{number}. {name}")

        elif sub == "view" and len(args) == 2:
            request = self.require_request(args[1])
            print(f"Request: {request.name}")
            print("Books:")
            for title, quantity in request.books.items():
                print(f"- {title}: {quantity}")

        elif sub == "gap" and len(args) == 2:
            request = self.require_request(args[1])
            missing = self.request_gap(args[1])
            if not missing:
                print(f"No missing copies for '{request.name}'.")
            else:
                print(f"Missing copies for '{request.name}':")
                for title, quantity in missing.items():
                    print(f"- {title}: {quantity}")

        elif sub == "lend" and len(args) == 2:
            request = self.require_request(args[1])
            missing = self.request_gap(args[1])
            if missing:
                print(f"Cannot lend '{request.name}'. Missing copies:")
                for title, quantity in missing.items():
                    print(f"- {title}: {quantity}")
            else:
                self.lend_request(args[1])
                self.save_holdings()
                print(f"Successfully lent '{request.name}'. "
                      "Holdings have been updated.")
        else:
            raise ValueError(
                'Invalid request command. Use: request list | '
                'request view|gap|lend "<name>"'
            )

    def _books_command(self, args):
        """Handle books add / return / process."""
        sub = args[0].lower() if args else ""

        if sub in ("add", "return") and len(args) == 3:
            title = args[1]
            quantity = self.parse_quantity(args[2])
            if sub == "add":
                self.add_book(title, quantity)
                print(f"Successfully added {quantity} of '{title}'.")
            else:
                self.return_book(title, quantity)
                print(f"Successfully returned {quantity} of '{title}'.")
            self.save_holdings()

        elif sub == "process" and len(args) == 2:
            self.process_file(args[1])
        else:
            raise ValueError(
                'Invalid books command. Use: books add|return "<title>" <qty> '
                '| books process <file>'
            )

    #  batch processing

    def parse_batch_line(self, line):
        """Split a batch line into (ACTION, title, quantity).

        The first word is the action, the last word is the quantity, and
        everything between them is the title (quotes optional).
        """
        command, _, rest = line.partition(" ")
        action = command.upper()
        if action not in ("ADD", "RETURN"):
            raise ValueError(f"Unknown command '{command}'.")

        title_part, _, quantity_text = rest.strip().rpartition(" ")
        title = title_part.strip().strip('"').strip()
        if not title:
            raise ValueError(f"Invalid line: {line}")
        return action, title, self.parse_quantity(quantity_text)

    def process_file(self, filepath):
        """Run a batch file line by line and write the report."""
        try:
            with open(filepath, "r", encoding="utf-8") as file:
                lines = file.read().splitlines()
        except FileNotFoundError:
            raise ValueError(f"Batch file '{filepath}' not found.")

        report = []
        for line in lines:
            line = line.strip()
            if not line:
                continue
            try:
                action, title, quantity = self.parse_batch_line(line)
                if action == "ADD":
                    self.add_book(title, quantity)
                else:
                    self.return_book(title, quantity)
                report.append(f"SUCCESS: {line}")
            except ValueError as error:
                report.append(f"ERROR: {error}")

        self.save_holdings()

        folder = os.path.dirname(self.report_path)
        if folder:
            os.makedirs(folder, exist_ok=True)
        with open(self.report_path, "w", encoding="utf-8") as file:
            file.write("".join(f"{entry}\n" for entry in report))

        print(f"Batch processing complete."
              f"See '{self.report_path}' for details.")

    # interactive mode

    def run_interactive(self):
        """Run the interactive session until the user types exit."""
        while True:
            try:
                line = input("> ").strip()
            except (EOFError, KeyboardInterrupt):
                line = "exit"

            if not line:
                continue

            if line.lower() == "exit":
                self.save_holdings()
                print("Holdings saved. Goodbye!")
                break

            try:
                tokens = shlex.split(line)
            except ValueError:
                print("Error: unbalanced quotes in command.")
                continue

            self.execute(tokens)
