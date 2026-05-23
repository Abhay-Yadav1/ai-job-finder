# test.py
from parsers import extract_text_from_file
test_filename = "app/utils/Abhay_resume_final (2).pdf"

try:
    # 2. Read the file locally as raw bytes (rb = read binary)
    with open(test_filename, "rb") as f:
        file_bytes = f.read()
    
    # 3. Pass the bytes and the filename to your helper function
    extracted_text = extract_text_from_file(file_bytes, test_filename)
    
    print("--- EXTRACTION SUCCESSFUL ---")
    print(extracted_text[:500]) # Print just the first 500 characters so it doesn't flood your screen
    
except Exception as e:
    print(f"Error during testing: {e}")