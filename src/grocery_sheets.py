import os
import re
import json

from utils.config import Config
from utils.logging import logger
from google.oauth2 import service_account
from googleapiclient.discovery import build

config = Config()

def initialize_sheet(service, sheet_name):
    """Creates headers and optionally a named range (table) in the sheet."""
    try:
        # Check if headers already exist (optional, but good practice)
        header_range = f"{sheet_name}!A1:F1"  # Adjust range if you have more columns
        header_values = service.spreadsheets().values().get(
            spreadsheetId=config.get('SPREADSHEET_ID'), range=header_range).execute().get('values', [])

        if not header_values:  # Create headers if they don't exist
            header_values = [["Original Item Name", "Item Name", "Quantity", "Unit", "Price", "Value"]]
            header_body = {'values': header_values}
            service.spreadsheets().values().update(
                spreadsheetId=config.get('SPREADSHEET_ID'), range=header_range,
                valueInputOption='USER_ENTERED', body=header_body).execute()
            logger.info("Headers created in Google Sheet.")
        else:
            logger.info("Headers already exist.")

        # # Create a named range (table) - Optional
        # named_range_name = "grocery_tracker"

        # # 1. Get existing named ranges (to check if it exists)
        # named_ranges_response = service.spreadsheets().get(spreadsheetId=config.get('SPREADSHEET_ID')).execute()
        # named_ranges = named_ranges_response.get('namedRanges', [])

        # named_range_id = None
        # for nr in named_ranges:
        #     if nr.get('name') == named_range_name:
        #         named_range_id = nr.get('namedRangeId')
        #         break

        # # 2. Prepare the named range request body
        # request_body = {
        #     "name": named_range_name,
        #     "range": {
        #         "sheetId": 0,  # Index of the sheet (usually 0)
        #         "startRowIndex": 1,  # Start from the second row (after headers)
        #         "endRowIndex": 2,  # Initial end row (will be updated later)
        #         "startColumnIndex": 0,
        #         "endColumnIndex": 6
        #     }
        # }

        # # 3. Get the current number of rows (to update endRowIndex)
        # values_response = service.spreadsheets().values().get(
        #     spreadsheetId=config.get('SPREADSHEET_ID'), range=f"{sheet_name}!A:F").execute()
        # num_rows = len(values_response.get('values', [])) + 1 if values_response.get('values') else 2

        # request_body["range"]["endRowIndex"] = num_rows

        # # 4. Create or update the named range
        # if named_range_id:
        #     # Update
        #     service.spreadsheets().namedranges().update(
        #         spreadsheetId=config.get('SPREADSHEET_ID'),
        #         namedRangeId=named_range_id,
        #         body=request_body).execute()
        #     logger.info(f"Named range '{named_range_name}' updated.")
        # else:
        #     # Create
        #     service.spreadsheets().namedranges().create(
        #         spreadsheetId=config.get('SPREADSHEET_ID'),
        #         body=request_body).execute()
        #     logger.info(f"Named range '{named_range_name}' created.")

    except Exception as e:
        logger.exception("Error initializing sheet:")
        return False
    return True

def write_to_sheet(data):
    """Writes the extracted grocery data to a Google Sheet."""

    try:      
        credentials = service_account.Credentials.from_service_account_info(config.get('GOOGLE_SERVICE_INFO'))
        service = build('sheets', 'v4', credentials=credentials)

        if not initialize_sheet(service, config.get('SHEET_NAME')): # Initialize headers and table
            return False
        
        # Convert the data to a list of lists (required by the Sheets API)
        values = []
        for item in data["items"]:
            values.append([
                item["original_item_name"],
                item["item_name"],
                item["quantity"],
                item["unit"],
                item["price"],
                item["value"]
            ])

        # Write the data to the sheet (append to the end)
        body = {
            'values': values
        }

        result = service.spreadsheets().values().append(
            spreadsheetId=config.get('SPREADSHEET_ID'), range=f"{config.get('SHEET_NAME')}!A:F",  # Adjust range as needed
            valueInputOption='USER_ENTERED', body=body).execute()

        logger.info(f"{len(values)} rows appended to Google Sheet.")
        return True

    except Exception as e:
        logger.exception("Error writing to Google Sheet:")
        logger.exception(e)
        return False

if __name__ == "__main__":
    # Load the data from the JSON file
    with open("receipt_data.json", "r") as f:
        data = json.load(f)

    # Write the data to the Google Sheet
    write_to_sheet(data)