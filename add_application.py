import argparse
import json
import sys
from auth import get_credentials, build_service

CONFIG_FILE = 'config.json'
STATUS_OPTIONS = ['Pending', 'Needs Calling', 'Ready', 'Declined', 'Approved', 'Interviewed']
STATUS_LOWER = {s.lower(): s for s in STATUS_OPTIONS}


def load_config() -> dict:
    try:
        with open(CONFIG_FILE) as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: '{CONFIG_FILE}' not found. Run 'python setup.py' first to create the spreadsheet.")
        sys.exit(1)


def get_sheet_title(service, spreadsheet_id: str) -> str:
    result = service.spreadsheets().get(
        spreadsheetId=spreadsheet_id,
        fields='sheets.properties.title'
    ).execute()
    return result['sheets'][0]['properties']['title']


def validate_status(value: str) -> str:
    normalized = STATUS_LOWER.get(value.strip().lower())
    if normalized is None:
        valid = ', '.join(STATUS_OPTIONS)
        raise argparse.ArgumentTypeError(f"Invalid status '{value}'. Choose from: {valid}")
    return normalized


def append_row(service, spreadsheet_id: str, sheet_title: str, name: str, position: str,
               salary: str, status: str, phone: str = '') -> int:
    row = [name, position, salary, status, phone]
    result = service.spreadsheets().values().append(
        spreadsheetId=spreadsheet_id,
        range=f'{sheet_title}!A:E',
        valueInputOption='RAW',
        insertDataOption='INSERT_ROWS',
        body={'values': [row]}
    ).execute()
    updated_range = result.get('updates', {}).get('updatedRange', '')
    # Extract row number from range string like "Sheet1!A5:E5"
    try:
        row_num = int(updated_range.split('!')[1].split(':')[0][1:])
    except (IndexError, ValueError):
        row_num = -1
    return row_num


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Add a job application to the spreadsheet.')
    parser.add_argument('--name',     required=True,  help='Company name')
    parser.add_argument('--position', required=True,  help='Job position')
    parser.add_argument('--salary',   required=True,  help='Salary (e.g. 120000 or "120,000")')
    parser.add_argument('--status',   required=True,  type=validate_status,
                        help=f'Status: {", ".join(STATUS_OPTIONS)}')
    parser.add_argument('--phone',    default='',     help='Phone number (optional)')
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = load_config()
    spreadsheet_id = config['spreadsheet_id']

    creds = get_credentials()
    service = build_service(creds)

    sheet_title = get_sheet_title(service, spreadsheet_id)
    row_num = append_row(service, spreadsheet_id, sheet_title, args.name, args.position,
                         args.salary, args.status, args.phone)

    if row_num > 0:
        print(f"Added '{args.name}' ({args.position}) at row {row_num}.")
    else:
        print(f"Added '{args.name}' ({args.position}) to the spreadsheet.")


if __name__ == '__main__':
    main()
