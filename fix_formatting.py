import json
from auth import get_credentials, build_service

STATUS_OPTIONS = ['Pending', 'Needs Calling', 'Ready', 'Declined', 'Approved', 'Interviewed']

STATUS_COLORS = {
    'Pending':       {'red': 0.62,  'green': 0.62,  'blue': 0.62},
    'Needs Calling': {'red': 1.0,   'green': 0.922, 'blue': 0.231},
    'Ready':         {'red': 0.298, 'green': 0.686, 'blue': 0.314},
    'Approved':      {'red': 0.647, 'green': 0.847, 'blue': 0.655},
    'Interviewed':   {'red': 1.0,   'green': 0.596, 'blue': 0.0},
    'Declined':      {'red': 0.957, 'green': 0.263, 'blue': 0.212},
}


def main():
    with open('config.json') as f:
        config = json.load(f)
    spreadsheet_id = config['spreadsheet_id']

    creds = get_credentials()
    service = build_service(creds)

    result = service.spreadsheets().get(
        spreadsheetId=spreadsheet_id,
        fields='sheets.properties,sheets.conditionalFormats'
    ).execute()
    sheet = result['sheets'][0]
    sheet_id = sheet['properties']['sheetId']
    num_existing_rules = len(sheet.get('conditionalFormats', []))

    requests = []

    # Remove all existing conditional format rules
    for _ in range(num_existing_rules):
        requests.append({
            'deleteConditionalFormatRule': {'sheetId': sheet_id, 'index': 0}
        })

    # Reset data row backgrounds to white (clears any lingering row colors)
    requests.append({
        'repeatCell': {
            'range': {
                'sheetId': sheet_id,
                'startRowIndex': 1,
                'startColumnIndex': 0,
                'endColumnIndex': 5,
            },
            'cell': {
                'userEnteredFormat': {
                    'backgroundColor': {'red': 1.0, 'green': 1.0, 'blue': 1.0}
                }
            },
            'fields': 'userEnteredFormat.backgroundColor'
        }
    })

    # Re-apply data validation (fixes the dropdown)
    requests.append({
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
    })

    # Add new conditional format rules — Status cell only (column D)
    for i, status in enumerate(STATUS_OPTIONS):
        requests.append({
            'addConditionalFormatRule': {
                'rule': {
                    'ranges': [{
                        'sheetId': sheet_id,
                        'startRowIndex': 1,
                        'startColumnIndex': 3,
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

    print('Done! Formatting and dropdown updated.')


if __name__ == '__main__':
    main()
