import os
import re
import json

import PIL.Image

from google import genai

# gemini_api_key = os.environ.get("GEMINI_API_KEY")
gemini_api_key = "gemini_api_key.txt"

# Load Gemini API key from secret file
if gemini_api_key:
    try:
        with open(gemini_api_key, "r") as f:
            gemini_api_key = f.read().strip()  # Read and remove any whitespace
        print("Gemini API key loaded from secret.")
        client = genai.Client(api_key=gemini_api_key)
    except FileNotFoundError:
        print("Gemini API key file not found. Did you create the secret and mount it?")
    except Exception as e:
        print(f"Error reading Gemini API key: {e}")
else:
    print("gemini_api_key environment variable not set.")

def perform_ocr_gemini(image_path):
    """Performs OCR using Gemini's vision capabilities."""
    try:
        encoded_image = PIL.Image.open(image_path)

        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=["Extract the text from this receipt:", encoded_image]
        )

        extracted_text = response.text
        return extracted_text

    except Exception as e:
        print(f"Gemini OCR Error: {e}")
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
    print("Gemini client not initialized. Exiting.")
    exit()

OCR = perform_ocr_gemini("receipt_1.jpg")

response = client.models.generate_content(
    model="gemini-2.0-flash",
    contents=prompt + OCR,
)

output = response.text
try:
    # 1. Clean the output (using regex to find JSON object)
    match = re.search(r"\{.*\}", output, re.DOTALL) # Find JSON object
    if match:
        cleaned_output = match.group(0).strip()
    else:
        print("Could not find JSON object in Gemini output.")

    # 2. Robust JSON parsing
    data = json.loads(cleaned_output)
    
    # 3. Save to JSON file
    with open("receipt_data.json", "w") as f:
        json.dump(data, f, indent=4)  # indent for pretty formatting
    print("Data saved to receipt_data.json")

except json.JSONDecodeError as e:
    print(f"JSON Decode Error: {e}")
    print("Raw Output:", output)  # Print for debugging
    print("Cleaned Output:", cleaned_output) # Print for debugging

except Exception as e: # Catch other potential errors
    print(f"An unexpected error occurred: {e}")