"""Entry point for LoanDesk."""

import json
import sys
"""json read and write json files and sys Accesses command-line arguments"""
from loandesk.holdings import Holdings
from loandesk.manager import LoanDeskManager
from loandesk.requests import Request


def main():
    """Load the data, then run interactive mode or a single command."""
    try:
        with open("config.json", "r", encoding="utf-8") as file:
            config = json.load(file)
        holdings = Holdings.load(config["holdings_file"])
        requests = Request.load_all(config["request_file"])
    except FileNotFoundError as error:
        print(f"File not found: {error.filename}")
        return
    except (json.JSONDecodeError, KeyError) as error:
        print(f"Invalid config or data file: {error}")
        return

    manager = LoanDeskManager(
        holdings, requests, config["holdings_file"], config["report_file"]
    )

    args = sys.argv[1:]
    if not args:
        print("Usage: python main.py <command>  |  python main.py manage")
    elif args[0].strip().lower() == "manage" and len(args) == 1:
        manager.run_interactive()
    else:
        manager.execute(args)


if __name__ == "__main__":
    main()
