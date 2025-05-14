import os
import logging
import json
import base64
from datetime import datetime
from typing import Dict, Optional
from openai import OpenAI
from dotenv import load_dotenv
import PyPDF2

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class OpenAIPDFExtractor:
    def __init__(self):
        """Initialize the PDF data extractor with OpenAI model."""
        load_dotenv()

        # Configure OpenAI API
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")

        # Set environment variable for OpenAI SDK v1.x
        os.environ["OPENAI_API_KEY"] = api_key
        self.client = OpenAI()

        # Create logs directory if it doesn't exist
        self.logs_dir = "data/logs"
        os.makedirs(self.logs_dir, exist_ok=True)

    def encode_pdf_to_base64(self, pdf_path: str) -> str:
        """Encode PDF file to base64 string."""
        try:
            with open(pdf_path, "rb") as f:
                pdf_content = f.read()
            logger.info(f"Successfully read PDF file: {len(pdf_content)} bytes")
            return base64.b64encode(pdf_content).decode("utf-8")
        except Exception as e:
            logger.error(f"Error reading PDF file: {str(e)}")
            raise

    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extract text content from PDF file."""
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
                logger.info(f"Successfully extracted text from PDF: {len(text)} characters")
                return text
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {str(e)}")
            raise

    def analyze_pdf_content(self, pdf_path: str, prompt: Optional[str] = None) -> Dict:
        """Analyze PDF content using OpenAI's GPT-4 model."""
        try:
            if not prompt:
                prompt = """
                Extract financial information from the quarterly report and return ONLY a JSON object with no additional text or explanation.
                Important: Numbers shown in parentheses () in the financial statements should be treated as negative values.
                For example, if you see (1,000) it should be recorded as -1000 in the JSON output.
                
                CRITICAL INSTRUCTIONS:
                1. Only extract values from the LATEST \"03 months\" or \"3 months\" column in the financial statements.
                   - This might not be the first column
                   - Look for the most recent quarter's data
                   - Ignore previous quarter's 03 months data
                2. Focus ONLY on GROUP financials, not company financials
                   - Look for sections labeled as \"Group\" or \"Consolidated\"
                   - Ignore any sections labeled as \"Company\" or standalone entity
                3. Ignore any values from:
                   - \"06 months\" or \"6 months\" columns
                   - \"12 months\" or \"1 year\" columns
                   - Previous quarter's data
                   - Company-level financials
                
                IMPORTANT: All monetary values in the financial statements are in thousands (Rs. '000). When extracting, multiply all currency values by 1,000 so that the output JSON contains the true value (e.g., 23,458 should be output as 23458000).
                
                If a value is not found in the document or you are uncertain about it, use null instead of making assumptions.
                Do not calculate or estimate missing values - only include values that are explicitly stated in the document.
                
                The response must be a valid JSON object with the following structure:
                {
                    \"quarter\": \"Q1/Q2/Q3/Q4\",
                    \"year\": \"YYYY\",
                    \"financial_metrics\": {
                        \"revenue\": \"value\",
                        \"cost_of_goods_sold\": \"value\",
                        \"gross_profit\": \"value\",
                        \"other_income\": \"value\",
                        \"distribution_costs\": \"value\",
                        \"administrative_expenses\": \"value\",
                        \"operating_income\": \"value\",
                        \"finance_costs\": \"value\",
                        \"finance_income\": \"value\",
                        \"share_of_profit_equity_investee\": \"value\",
                        \"profit_before_tax\": \"value\",
                        \"tax_expense\": \"value\",
                        \"net_income\": \"value\",
                        \"eps_basic\": \"value\",
                        \"eps_diluted\": \"value\",
                        \"dividend_per_share\": \"value\"
                    }
                }
                Do not include any text before or after the JSON object. The response must be parseable JSON only.
                All monetary values should be numbers (not strings) and negative values should be represented with a minus sign.
                Use null for any values that are not explicitly stated in the document.
                """

            # Extract text from PDF
            pdf_text = self.extract_text_from_pdf(pdf_path)
            
            logger.info("Sending request to OpenAI API...")

            messages = [
                {
                    "role": "system",
                    "content": "You are a financial data extraction assistant. You must respond with valid JSON only, no additional text or explanation."
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "text", "text": pdf_text}
                    ]
                }
            ]

            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=messages,
                max_tokens=2048,
                temperature=0.2,
            )

            response_text = response.choices[0].message.content
            logger.info("Received response from OpenAI API")

            if not response_text:
                logger.error("Empty response received from model")
                return {"error": "Empty response from model"}

            try:
                # Clean the response text to ensure it's valid JSON
                cleaned_text = response_text.strip()
                if cleaned_text.startswith('```json'):
                    cleaned_text = cleaned_text[7:]
                if cleaned_text.endswith('```'):
                    cleaned_text = cleaned_text[:-3]
                cleaned_text = cleaned_text.strip()

                result_json = json.loads(cleaned_text)
                logger.info("Successfully parsed response as JSON")
                return result_json
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON response: {str(e)}")
                logger.debug(f"Raw response: {response_text}")
                return {"error": "Invalid JSON response", "raw_text": response_text}

        except Exception as e:
            logger.error(f"Error analyzing PDF content: {str(e)}")
            raise

    def save_analysis_to_file(self, results: Dict) -> str:
        """Save analysis results to a JSON file."""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"openai_analysis_{timestamp}.json"
            filepath = os.path.join(self.logs_dir, filename)

            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(results, f, indent=4, ensure_ascii=False)

            logger.info(f"Analysis saved to: {filepath}")
            return filepath
        except Exception as e:
            logger.error(f"Error saving analysis to file: {str(e)}")
            raise

    def process_pdf(self, pdf_path: str, custom_prompt: Optional[str] = None) -> Dict:
        """Process a PDF file and extract relevant information."""
        try:
            logger.info(f"Processing PDF: {pdf_path}")
            analysis = self.analyze_pdf_content(pdf_path, custom_prompt)

            results = {
                "file_path": pdf_path,
                "analysis": analysis,
                "timestamp": datetime.now().isoformat(),
            }

            self.save_analysis_to_file(results)
            return results
        except Exception as e:
            logger.error(f"Error processing PDF {pdf_path}: {str(e)}")
            raise


def main():
    try:
        extractor = OpenAIPDFExtractor()
        pdf_path = "data/raw/pdfs/DIPD_2024_09_30.pdf"
        results = extractor.process_pdf(pdf_path)
        logger.info("PDF processing completed successfully")
        return results
    except Exception as e:
        logger.error(f"Error in main execution: {str(e)}")
        raise


if __name__ == "__main__":
    main()
