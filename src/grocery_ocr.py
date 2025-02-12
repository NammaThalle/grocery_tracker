import os
import re
import json
from utils.logging import logger

import PIL.Image
from google import genai

# Load Gemini API key from secret file (using environment variable for path)
# gemini_api_key_file = os.environ.get("GEMINI_API_KEY_FILE")
# TODO: Remove this implementation and stick to environemnt variables
gemini_api_key_file = "gemini_api_key.txt"

if not gemini_api_key_file:
    logger.error("GEMINI_API_KEY_FILE environment variable not set.")
    exit(1)  # Exit with error code

try:
    with open(gemini_api_key_file, "r") as f:
        gemini_api_key = f.read().strip()
    logger.info("Gemini API key loaded from secret.")
    client = genai.Client(api_key=gemini_api_key)
except FileNotFoundError:
    logger.error("Gemini API key file not found. Did you create the secret and mount it?")
    exit(1)
except Exception as e:
    logger.exception("Error reading Gemini API key:")  # Log the full exception details
    exit(1)

def perform_ocr_gemini(image_path):
    """Performs OCR using Gemini's vision capabilities."""
    try:
        encoded_image = PIL.Image.open(image_path)
        logger.info("Image loaded successfully.")

        logger.info("Performing OCR...")
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=["Extract the text from this receipt:", encoded_image]
        )

        extracted_text = response.text
        logger.info("OCR completed successfully.")

        return extracted_text

    except Exception as e:
        logger.exception(f"OCR Error:")  # Log the exception
        logger.exception(e)
        return None

prompt = '''
You are a receipt data extraction expert.  You will receive the OCR output of a grocery receipt.  Your task is to extract the relevant information and format it as a JSON object.  The JSON object should have the following keys (and ONLY these keys):
*   `store_name`: The name of the grocery store.
*   `store_location`: The location of the grocery store (city, state, etc.).
*   `purchase_date`: The date of purchase in YYYY-MM-DD format.
*   `purchase_time`: The time of purchase in HH:MM format (24-hour clock).
*   `items`: An array of JSON objects. Each object in the array represents a grocery item and should have the following keys:
    *   `original_item_name`: The exact item name as it appears on the receipt (the OCR text).
    *   `item_name`: A normalized or standardized version of the item name (e.g., "Milk" instead of "GOA DAIRY MILK-500").
    *   `quantity`: The quantity of the item (as a number).
    *   `unit`: The unit of measurement (e.g., "ml", "g", "kg", "unit"). If no unit is explicitly mentioned, use "unit".
    *   `price`: The price per unit of the item.
    *   `value`: The total value of the item (quantity * price).

Do not include any other information in the JSON object.  If a field is not present in the OCR output, leave it blank (but include the key).  If you are unsure of the value for a field, leave it blank.  Do your best to infer units (e.g., from "MILK-500" infer "ml").

Here is the OCR text of the receipt:

'''

if client is None:
    logger.error("Gemini client not initialized. Exiting.")
    exit(1)

def extract_and_save_data(image_path, output_file="receipt_data.json"):
    """Extracts data from a receipt image and saves it to a JSON file."""
    ocr_text = perform_ocr_gemini(image_path)

    if ocr_text is None:
        logger.error("OCR failed.")
        return False  # Indicate failure
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt + ocr_text,
        )
        output = response.text
        logger.info("Data extraction completed successfully.")
    except Exception as e:
        logger.exception(f"Could not convert response to JSON:")
        logger.exception(e)
        return False

    try:
        match = re.search(r"\{.*\}", output, re.DOTALL)
        if not match:
            logger.error("Could not find JSON object in Gemini output.")
            return False

        cleaned_output = match.group(0).strip()
        data = json.loads(cleaned_output)

        with open(output_file, "w") as f:
            json.dump(data, f, indent=4)
        logger.info(f"Data saved to {output_file}")
        return True

    except json.JSONDecodeError as e:
        logger.error(f"JSON Decode Error: {e}")
        logger.error(f"Raw Output: {output}")
        logger.error(f"Cleaned Output: {cleaned_output if 'cleaned_output' in locals() else 'N/A'}") # Conditional logging
        return False
    except Exception as e:
        logger.exception("An unexpected error occurred:") # Log the exception
        return False

if __name__ == "__main__": 
    image_path = "receipt_1.jpg"
    if extract_and_save_data(image_path):
        logger.info("Receipt processing completed successfully.")
    else:
        logger.error("Receipt processing failed.")
    
