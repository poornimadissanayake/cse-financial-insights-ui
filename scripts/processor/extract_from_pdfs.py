import os
import json
import re
from openai_data_extractor import OpenAIPDFExtractor

def correct_quarter_and_year_from_filename(filename, extracted_data):
    # Try to extract year and quarter from filename (e.g., Q1-2023)
    match = re.search(r"(Q[1-4])-(\d{4})", filename)
    if match:
        quarter, year = match.groups()
        extracted_data["quarter"] = quarter
        extracted_data["year"] = year
        return extracted_data

    # Try to extract year and date (e.g., 2023-03-31)
    match = re.search(r"(\d{4})[-_](\d{2})[-_](\d{2})", filename)
    if match:
        year, month, day = match.groups()
        if month == "03" and day == "31":
            quarter = "Q1"
        elif month == "06" and day == "30":
            quarter = "Q2"
        elif month == "09" and day == "30":
            quarter = "Q3"
        elif month == "12" and day == "31":
            quarter = "Q4"
        else:
            quarter = extracted_data.get("quarter", "")
        extracted_data["quarter"] = quarter
        extracted_data["year"] = year
    return extracted_data

def process_pdfs(pdf_dir: str) -> None:
    """
    Process all PDF files in the specified directory using OpenAI extractor.

    Args:
        pdf_dir (str): Directory containing PDF files
    """
    # Initialize OpenAI extractor
    extractor = OpenAIPDFExtractor()
    
    # Create output directory if it doesn't exist
    output_dir = "data/processed/jsons"
    os.makedirs(output_dir, exist_ok=True)
    
    # Process each PDF file
    for file in os.listdir(pdf_dir):
        if file.endswith(".pdf"):
            try:
                pdf_path = os.path.join(pdf_dir, file)
                print(f"Processing {file}...")
                
                # Extract data using OpenAI
                results = extractor.analyze_pdf_content(pdf_path)
                
                # Correct quarter and year based on filename
                results = correct_quarter_and_year_from_filename(file, results)
                
                # Create output filename (replace .pdf with .json)
                output_filename = file.replace(".pdf", ".json")
                output_path = os.path.join(output_dir, output_filename)
                
                # Save results to JSON file
                with open(output_path, "w", encoding="utf-8") as f:
                    json.dump(results, f, ensure_ascii=False, indent=2)
                
                print(f"Saved extracted data to {output_path}")
                
            except Exception as e:
                print(f"Error processing {file}: {str(e)}")

if __name__ == "__main__":
    # Path to the raw PDFs directory
    pdf_dir = "data/raw/pdfs"
    
    # Process all PDFs
    process_pdfs(pdf_dir)
