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
