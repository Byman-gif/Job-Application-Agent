import json
from auth import get_credentials, build_service

CONFIG_FILE = 'config.json'
SPREADSHEET_TITLE = 'Job Applications'
HEADERS = ['Name', 'Position', 'Salary', 'Status', 'Phone Number']

STATUS_OPTIONS = ['Pending', 'Needs Calling', 'Ready', 'Declined', 'Approved', 'Interviewed']

# Background colors (RGB 0-1 float scale) for each status
STATUS_COLORS = {
    'Pending':       {'red': 0.62,  'green': 0.62,  'blue': 0.62},
    'Needs Calling': {'red': 1.0,   'green': 0.922, 'blue': 0.231},
    'Ready':         {'red': 0.298, 'green': 0.686, 'blue': 0.314},
    'Approved':      {'red': 0.647, 'green': 0.847, 'blue': 0.655},
    'Interviewed':   {'red': 1.0,   'green': 0.596, 'blue': 0.0},
    'Declined':      {'red': 0.957, 'green': 0.263, 'blue': 0.212},
}


def create_spreadsheet(service) -> tuple[str, int, str]:
    body = {'properties': {'title': SPREADSHEET_TITLE}}
    result = service.spreadsheets().create(body=body, fields='spreadsheetId,sheets').execute()
    spreadsheet_id = result['spreadsheetId']
    sheet_props = result['sheets'][0]['properties']
    sheet_id = sheet_props['sheetId']
    sheet_title = sheet_props['title']
    return spreadsheet_id, sheet_id, sheet_title


def write_headers(service, spreadsheet_id: str, sheet_title: str) -> None:
    service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id,
        range=f'{sheet_title}!A1:E1',
        valueInputOption='RAW',
        body={'values': [HEADERS]}
    ).execute()


def format_header_row(service, spreadsheet_id: str, sheet_id: int) -> None:
    service.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body={'requests': [{
            'repeatCell': {
                'range': {
                    'sheetId': sheet_id,
                    'startRowIndex': 0,
                    'endRowIndex': 1,
                },
                'cell': {
                    'userEnteredFormat': {
                        'backgroundColor': {'red': 0.85, 'green': 0.85, 'blue': 0.85},
                        'textFormat': {'bold': True},
                    }
                },
                'fields': 'userEnteredFormat(backgroundColor,textFormat)',
            }
        }]}
    ).execute()


def add_data_validation(service, spreadsheet_id: str, sheet_id: int) -> None:
    service.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body={'requests': [{
            'setDataValidation': {
                'range': {
                    'sheetId': sheet_id,
                    'startRowIndex': 1,
                    'startColumnIndex': 3,
                    'endColumnIndex': 4,
                },
                'rule': {
                    'condition': {
                        'type': 'ONE_OF_LIST',
                        'values': [{'userEnteredValue': s} for s in STATUS_OPTIONS],
                    },
                    'strict': True,
                    'showCustomUi': True,
                }
            }
        }]}
    ).execute()


def add_conditional_formatting(service, spreadsheet_id: str, sheet_id: int) -> None:
    requests = []
    for i, status in enumerate(STATUS_OPTIONS):
        requests.append({
            'addConditionalFormatRule': {
                'rule': {
                    'ranges': [{
                        'sheetId': sheet_id,
                        'startRowIndex': 1,
                        'startColumnIndex': 3,  # column D only
                        'endColumnIndex': 4,
                    }],
                    'booleanRule': {
                        'condition': {
                            'type': 'TEXT_EQ',
                            'values': [{'userEnteredValue': status}],
                        },
                        'format': {
                            'backgroundColor': STATUS_COLORS[status],
                        }
                    }
                },
                'index': i,
            }
        })
    service.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body={'requests': requests}
    ).execute()


def save_config(spreadsheet_id: str) -> None:
    with open(CONFIG_FILE, 'w') as f:
        json.dump({'spreadsheet_id': spreadsheet_id}, f, indent=2)


def main() -> None:
    print('Authenticating with Google...')
    creds = get_credentials()
    service = build_service(creds)

    print('Creating spreadsheet...')
    spreadsheet_id, sheet_id, sheet_title = create_spreadsheet(service)

    print('Writing headers...')
    write_headers(service, spreadsheet_id, sheet_title)

    print('Formatting header row...')
    format_header_row(service, spreadsheet_id, sheet_id)

    print('Adding status dropdown...')
    add_data_validation(service, spreadsheet_id, sheet_id)

    print('Adding color-coded conditional formatting...')
    add_conditional_formatting(service, spreadsheet_id, sheet_id)

    save_config(spreadsheet_id)

    url = f'https://docs.google.com/spreadsheets/d/{spreadsheet_id}/edit'
    print(f'\nDone! Your spreadsheet is ready:\n{url}')


if __name__ == '__main__':
    main()
