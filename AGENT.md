## About Project

I want you to help me create a google spreadsheet about job applications
It has a clickdown that dictates the current job applications status pending, needs calling, ready, declined, approved, interviewd that are color coded
After i give you information about the job application as text i want you to add it to the spreadsheet in different colums:

Name: has the companys name
Position: has the companys position they are hiring
Salary: Has the salary
The status clickdown
Number i can call about the job if it has one

---

## Setup (one time)

1. Place `credentials.json` (from Google Cloud Console) in this directory
2. Run: `pip install -r requirements.txt`
3. Run: `python setup.py` — a browser window opens for Google login, then the spreadsheet is created and its URL is printed

## Adding a Job Application

When the user describes a job application in natural language, parse it and run:

```
python add_application.py --name "<company>" --position "<position>" --salary "<salary>" --status "<status>" --phone "<phone>"
```

`--phone` is optional. `--status` must be one of: `Pending`, `Needs Calling`, `Ready`, `Declined`, `Approved`, `Interviewed`

### Archiving the full job description

When the user pastes the full text of a job posting (not just a short summary), archive it so it can still be
found after the posting is taken down:

1. Write the pasted text verbatim to a temp file (e.g. in the scratchpad directory).
2. Pass it with `--description-file <path>` (and `--url "<posting URL>"` if one was given).

```
python add_application.py --name "<company>" --position "<position>" --salary "<salary>" --status "<status>" --description-file "<temp file path>" --url "<posting url>"
```

This copies the text into `job_descriptions/<date>_<company>_<position>.txt` and records that path in the
spreadsheet's `Description File` column. `job_descriptions/` is local-only (gitignored) — it is not synced
anywhere else, so treat it as the durable copy.

### Status color codes
| Status | Color |
|---|---|
| Pending | Yellow |
| Needs Calling | Orange |
| Ready | Blue |
| Declined | Red |
| Approved | Green |
| Interviewed | Purple |

### Example
User says: "Got a reply from Google, Software Engineer, 180k, still pending, call 050-9876543"

Run:
```
python add_application.py --name "Google" --position "Software Engineer" --salary "180000" --status "Pending" --phone "050-9876543"
```
