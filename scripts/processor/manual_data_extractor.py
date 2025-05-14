import pdfplumber
import re


def split_line_into_columns(line):
    # Remove spaces between parentheses and numbers, e.g., '( 8)' -> '(8)'
    line = re.sub(r'\(\s+(\d)', r'(\1', line)
    line = re.sub(r'(\d)\s+\)', r'\1)', line)
    # Remove spaces before commas in numbers, e.g., '7 ,88' -> '7,88'
    line = re.sub(r'(\d)\s+,\s*(\d)', r'\1,\2', line)
    # First, find the text part (letters, spaces, and special characters)
    text_match = re.match(r"^([A-Za-z /&\(\)\-]+)", line)
    if not text_match:
        return None

    text = text_match.group(1).strip()

    # Find all numbers in the line
    numbers = re.findall(r"[-]?\(?[\d,]+\)?", line)

    # Clean up numbers (remove commas, convert parentheses to negative signs)
    cleaned_numbers = []
    for num in numbers:
        cleaned = num.replace(",", "").replace("(", "-").replace(")", "")
        cleaned_numbers.append(cleaned)

    # print(text, cleaned_numbers)

    return {"text": text, "numbers": cleaned_numbers}


def read_pdf_line_by_line(pdf_path):
    # Pattern to match lines containing both letters and numbers
    pattern = re.compile(r"(?=.*[A-Za-z])(?=.*\d)")

    with pdfplumber.open(pdf_path) as pdf:
        # Iterate through each page
        for page_num, page in enumerate(pdf.pages, 1):
            print(f"\n=== Page {page_num} ===")

            # Extract text from the page
            text = page.extract_text()
            if text:
                # Split into lines and process those with both letters and numbers
                for line_num, line in enumerate(text.split("\n"), 1):
                    if pattern.search(line):
                        columns = split_line_into_columns(line)
                        if columns:
                            # Format the output - only show first and fifth columns
                            text_col = columns["text"].ljust(
                                40
                            )  # Left align text column
                            value = (
                                columns["numbers"][-3]
                                if len(columns["numbers"]) > 4
                                else "N/A"
                            )
                            print(f"Line {line_num}: {text_col} | {value}")


if __name__ == "__main__":
    pdf_file = "data/raw/pdfs/DIPD_2024_03_31.pdf"
    read_pdf_line_by_line(pdf_file)
