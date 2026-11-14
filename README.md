# LoanDesk 📚

A Python command-line application for managing library books and reading-list requests. Track available copies, identify missing books, lend complete requests, and process inventory updates in batches.

## Features

- Track total, borrowed, and available copies of each book.
- List and view reading-list requests.
- Check which books are missing from a request.
- Find requests that can be fulfilled with current stock.
- Lend a complete request only when every required book is available.
- Add new copies and return borrowed books.
- Process batch commands and generate a results report.
- Save inventory changes in JSON files.
- Use individual commands or an interactive session.

Book titles and request names are matched without regard to case.

## Requirements

- Python 3 — verified with Python 3.12.
- No external dependencies; uses the Python standard library.

## Getting Started

Download or clone the project, then open a terminal in the folder containing `main.py`:

```bash
cd loandesk_project
python main.py request list
```

If your system uses `python3`, replace `python` with `python3` in the commands below.

Run commands from the project root so the application can find `config.json` and the data files.

## Usage

### Interactive mode

```bash
python main.py manage
```

Enter commands at the prompt:

```text
request list
request view "Monday Seminar"
request gap "Monday Seminar"
plan
request lend "Monday Seminar"
books add "Hamlet" 2
books return "Hamlet" 1
exit
```

Use quotes around titles or request names containing spaces. Enter `exit` to save and close the session.

### Individual commands

| Command | Description |
| --- | --- |
| `python main.py request list` | List all reading-list requests. |
| `python main.py request view "Monday Seminar"` | Show the books and quantities in a request. |
| `python main.py request gap "Monday Seminar"` | Show missing copies for a request. |
| `python main.py plan` | List requests that can currently be fulfilled. |
| `python main.py request lend "Monday Seminar"` | Lend all books required by a request. |
| `python main.py books add "Hamlet" 2` | Add copies to the inventory. |
| `python main.py books return "Hamlet" 1` | Return borrowed copies. |
| `python main.py books process batch_commands.txt` | Process a batch file. |

The `plan` command checks each request independently against the current inventory. Its results do not mean all listed requests can be fulfilled together.

## Batch Processing

Create a text file with one operation per line:

```text
ADD Hamlet 2
RETURN "Brave New World" 1
ADD Dune 1
```

Run:

```bash
python main.py books process batch_commands.txt
```

Supported batch operations are `ADD` and `RETURN`. Blank lines are ignored. Invalid operations are recorded as errors, and processing continues with the remaining lines.

Successful changes are saved to the holdings file. The report is written to `reports/report.txt` by default, replacing the previous report.

The included sample batch file contains invalid operations to demonstrate error reporting.

## Configuration

File locations are defined in `config.json`:

```json
{
  "request_file": "data/requests.json",
  "holdings_file": "data/holdings.json",
  "report_file": "reports/report.txt"
}
```

### Holdings format

```json
{
  "Hamlet": {
    "copies": 5,
    "borrowed": 2
  }
}
```

Available copies are calculated as:

```text
available = copies - borrowed
```

### Request format

```json
[
  {
    "name": "Monday Seminar",
    "books": {
      "Hamlet": 3,
      "Brave New World": 1
    }
  }
]
```

Add or edit reading-list requests in `data/requests.json`.

## Project Structure

```text
loandesk_project/
├── main.py                 # Application entry point
├── config.json             # Data and report paths
├── batch_commands.txt      # Example batch operations
├── loandesk/
│   ├── __init__.py
│   ├── holdings.py          # Book inventory and lending logic
│   ├── manager.py           # Commands and interactive mode
│   ├── requests.py          # Reading-list request model
│   └── storage.py           # JSON loading and saving
├── data/
│   ├── holdings.json
│   └── requests.json
└── reports/
    └── report.txt
```

## Lending Rules

- Quantities must be positive whole numbers.
- A request is lent only if every required title has enough available copies.
- Lending increases borrowed counts.
- Returns decrease borrowed counts and cannot exceed the number borrowed.
- Adding books increases total copies.
- Successful lending, additions, and returns update the holdings file.

The application tracks borrowed quantities per title. It does not currently track individual borrowers, due dates, or loan histories.