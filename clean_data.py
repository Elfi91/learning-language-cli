import json
import os

FILE_PATH = 'errori.json'

def clean_errors():
    if not os.path.exists(FILE_PATH):
        print("File errori.json not found.")
        return

    try:
        with open(FILE_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"Total entries before cleaning: {len(data)}")
        
        # Filter out entries where explanation contains API errors
        cleaned_data = [
            entry for entry in data 
            if "RESOURCE_EXHAUSTED" not in entry.get("explanation", "") 
            and "Error generating explanation" not in entry.get("explanation", "")
        ]
        
        print(f"Total entries after cleaning: {len(cleaned_data)}")
        
        with open(FILE_PATH, 'w', encoding='utf-8') as f:
            json.dump(cleaned_data, f, indent=4, ensure_ascii=False)
            
        print("Successfully cleaned errori.json")

    except Exception as e:
        print(f"Error processing file: {e}")

if __name__ == "__main__":
    clean_errors()
