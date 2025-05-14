"""
Main scraper module for CSE financial data.
Handles the scraping of quarterly reports from CSE-listed companies.
"""

from datetime import datetime
from typing import List, Tuple
import logging
from pathlib import Path
import platform
import time
import re
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
from tqdm import tqdm
from dateutil import parser as date_parser

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class CSEScraper:
    """Scraper for Colombo Stock Exchange financial data."""

    BASE_URL = "https://www.cse.lk/pages/company-profile/company-profile.component.html"
    COMPANIES = {
        "DIPD": "DIPD.N0000",  # Dipped Products PLC
        "REXP": "REXP.N0000",  # Richard Pieris Exports PLC
    }
    YEARS_TO_LOOK_BACK = 5

    def __init__(self, output_dir: str = "data/raw"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.pdf_dir = self.output_dir / "pdfs"
        self.pdf_dir.mkdir(exist_ok=True)
        self._setup_selenium()
        self.request_delay = 2  # seconds between requests

    def _setup_selenium(self):
        try:
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            if platform.system() == "Darwin":
                chrome_options.binary_location = (
                    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
                )
                service = Service()
            else:
                service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            logger.info("Successfully initialized Chrome WebDriver")

            # Navigate to base URL and handle consent
            self.driver.get(self.BASE_URL)
            time.sleep(3)  # Wait for page to load

            try:
                consent_button = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable(
                        (
                            By.XPATH,
                            "//p[contains(@class, 'fc-button-label') and text()='Consent']",
                        )
                    )
                )
                consent_button.click()
                logger.info("Successfully clicked consent button")
                time.sleep(2)  # Wait for consent to be processed
            except TimeoutException:
                logger.warning("Consent button not found or not clickable")

        except Exception as e:
            logger.error(f"Error setting up Selenium: {str(e)}")
            raise

    def _get_company_url(self, symbol: str) -> str:
        return f"{self.BASE_URL}?symbol={symbol}"

    def _wait_for_element(self, by: By, value: str, timeout: int = 10):
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, value))
            )
            return element
        except TimeoutException:
            logger.warning(f"Timeout waiting for element: {value}")
            return None

    def _click_financials_tab(self):
        try:
            time.sleep(3)
            active_tab = self.driver.find_elements(
                By.XPATH,
                "//a[contains(@class, 'active') and contains(text(), 'Financials')]",
            )
            if active_tab:
                logger.info("Financials tab is already active.")
                return True
            financials_tab = self.driver.find_element(
                By.XPATH, "//a[contains(text(), 'Financials')]"
            )
            self.driver.execute_script(
                "arguments[0].scrollIntoView(true);", financials_tab
            )
            time.sleep(1)
            financials_tab.click()
            time.sleep(2)
            logger.info("Clicked Financials tab.")
            return True
        except Exception as e:
            logger.error(f"Error clicking Financials tab: {str(e)}")
            return False

    def _click_quarterly_reports_tab(self):
        try:
            qr_tab = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable(
                    (
                        By.XPATH,
                        "//button[contains(text(), 'Quarterly Reports')] | //div[contains(@class, 'tab') and contains(text(), 'Quarterly Reports')] | //a[contains(text(), 'Quarterly Reports')]",
                    )
                )
            )
            self.driver.execute_script("arguments[0].scrollIntoView(true);", qr_tab)
            time.sleep(1)
            qr_tab.click()
            time.sleep(2)
            logger.info("Clicked Quarterly Reports tab.")
            return True
        except Exception as e:
            logger.error(f"Error clicking Quarterly Reports tab: {str(e)}")
            return False

    def _get_quarterly_report_links(self) -> List[Tuple[str, str]]:
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(
                    (
                        By.XPATH,
                        "//*[contains(text(), 'Quarterly Reports') or contains(text(), 'Uploaded Date') or contains(text(), 'Report') or contains(@href, '.pdf') ]",
                    )
                )
            )
            rows = self.driver.find_elements(
                By.XPATH,
                "//div[contains(@class, 'tab-pane') and contains(@class, 'active')]//tr",
            )
            if not rows:
                rows = self.driver.find_elements(By.XPATH, "//tr")
            reports = []
            now = datetime.now()
            years_ago = now.replace(year=now.year - self.YEARS_TO_LOOK_BACK)
            
            # Add pagination handling if needed
            try:
                next_button = self.driver.find_element(By.XPATH, "//button[contains(@class, 'next') or contains(text(), 'Next')]")
                has_next = True
            except:
                has_next = False

            while True:
                for row in rows:
                    try:
                        date_cell = row.find_element(By.XPATH, ".//td[1]")
                        link_elem = row.find_element(
                            By.XPATH, ".//a[contains(@href, '.pdf')]"
                        )
                        report_date_str = date_cell.text.strip()
                        pdf_url = link_elem.get_attribute("href")
                        try:
                            report_date = date_parser.parse(report_date_str, fuzzy=True)
                        except Exception:
                            continue
                        if pdf_url and report_date and report_date >= years_ago:
                            reports.append((report_date_str, pdf_url))
                    except Exception:
                        continue

                if not has_next:
                    break

                try:
                    next_button.click()
                    time.sleep(self.request_delay)  # Wait for new page to load
                    rows = self.driver.find_elements(
                        By.XPATH,
                        "//div[contains(@class, 'tab-pane') and contains(@class, 'active')]//tr",
                    )
                    if not rows:
                        rows = self.driver.find_elements(By.XPATH, "//tr")
                except:
                    break

            if not reports:
                logger.warning(
                    f"No quarterly report PDF links found in the table (within last {self.YEARS_TO_LOOK_BACK} year(s))."
                )
            else:
                logger.info(
                    f"Found {len(reports)} quarterly report PDFs (last {self.YEARS_TO_LOOK_BACK} year(s)):"
                )
                for report_date, pdf_url in reports:
                    logger.info(f"  Date: {report_date} | URL: {pdf_url}")
            return reports
        except Exception as e:
            logger.error(f"Error getting quarterly report links: {str(e)}")
            return []

    def _download_pdf(self, url: str, filename: str) -> bool:
        try:
            response = requests.get(url)
            if response.status_code == 200:
                # Create a temporary file to store the full PDF
                temp_full_pdf = self.pdf_dir / f"temp_full_{filename}"
                with open(temp_full_pdf, "wb") as f:
                    f.write(response.content)

                # Extract date from the full PDF first
                company_code = filename.split("_")[0]
                date_str = self._extract_quarter_end_date_from_pdf(temp_full_pdf)

                if not date_str:
                    # If date extraction fails, use current timestamp as fallback
                    date_str = datetime.now().strftime("%Y_%m_%d")
                    logger.warning(
                        f"Could not extract date from PDF, using current date: {date_str}"
                    )

                # Extract only the required page based on company
                required_page = 3 if company_code == "DIPD" else 4

                try:
                    from PyPDF2 import PdfReader, PdfWriter

                    # Read the full PDF
                    reader = PdfReader(str(temp_full_pdf))  # Convert Path to string

                    # Check if the required page exists
                    if len(reader.pages) >= required_page:
                        # Create a new PDF with only the required page
                        writer = PdfWriter()
                        writer.add_page(
                            reader.pages[required_page - 1]
                        )  # -1 because pages are 0-indexed

                        # Save the single-page PDF with the extracted date
                        final_filename = f"{company_code}_{date_str}.pdf"
                        filepath = self.pdf_dir / final_filename
                        with open(filepath, "wb") as f:
                            writer.write(f)

                        logger.info(
                            f"Downloaded and extracted page {required_page} from PDF: {final_filename}"
                        )

                        # Clean up temporary file
                        if temp_full_pdf.exists():
                            temp_full_pdf.unlink()
                        return True
                    else:
                        logger.error(
                            f"PDF {filename} doesn't have enough pages. Required page {required_page} not found."
                        )
                        if temp_full_pdf.exists():
                            temp_full_pdf.unlink()
                        return False

                except Exception as e:
                    logger.error(f"Error processing PDF {filename}: {str(e)}")
                    if temp_full_pdf.exists():
                        temp_full_pdf.unlink()
                    return False

            return False
        except Exception as e:
            logger.error(f"Error downloading PDF {filename}: {str(e)}")
            return False

    def _extract_quarter_end_date_from_pdf(self, pdf_path: Path) -> str:
        try:
            if not pdf_path.exists():
                logger.error(f"PDF file does not exist: {pdf_path}")
                return None

            with open(pdf_path, "rb") as file:
                import PyPDF2

                pdf_reader = PyPDF2.PdfReader(file)
                if not pdf_reader.pages:
                    return None

                # Try to find date in first few pages
                for page_num in range(min(3, len(pdf_reader.pages))):
                    page = pdf_reader.pages[page_num]
                    text = page.extract_text() or ""

                    # Try multiple patterns to match different date formats
                    patterns = [
                        r"(?:ended|as at|for the period ended)[^\n\d]*(\d{1,2}(?:st|nd|rd|th)?\s+[A-Za-z]+\s+\d{4})",
                        r"(?:quarter|period)[^\n\d]*(\d{1,2}(?:st|nd|rd|th)?\s+[A-Za-z]+\s+\d{4})",
                        r"(?:as at|as of)[^\n\d]*(\d{1,2}(?:st|nd|rd|th)?\s+[A-Za-z]+\s+\d{4})",
                        r"(\d{1,2}(?:st|nd|rd|th)?\s+[A-Za-z]+\s+\d{4})",  # Fallback to any date
                    ]

                    for pattern in patterns:
                        match = re.search(pattern, text, re.IGNORECASE)
                        if match:
                            date_str = match.group(1)
                            # Clean up the date string
                            date_str = re.sub(r"(st|nd|rd|th)", "", date_str)
                            try:
                                dt = date_parser.parse(date_str, fuzzy=True)
                                return dt.strftime("%Y_%m_%d")
                            except Exception:
                                continue

                logger.warning(f"Could not extract date from PDF {pdf_path}")
                return None

        except Exception as e:
            logger.error(
                f"Error extracting quarter end date from PDF {pdf_path}: {str(e)}"
            )
            return None

    def scrape_company_data(self, company_code: str) -> None:
        symbol = self.COMPANIES.get(company_code)
        if not symbol:
            raise ValueError(f"Invalid company code: {company_code}")
        url = self._get_company_url(symbol)
        logger.info(f"Scraping data for {company_code} from {url}")
        try:
            self.driver.get(url)
            time.sleep(2)
            if not self._click_financials_tab():
                logger.error(f"Could not access Financials tab for {company_code}")
                return
            if not self._click_quarterly_reports_tab():
                logger.error(
                    f"Could not access Quarterly Reports tab for {company_code}"
                )
                return
            reports = self._get_quarterly_report_links()
            if not reports:
                logger.error(f"No quarterly reports found for {company_code}")
                return
            for report_date, pdf_url in reports:
                try:
                    # Try to parse the date from the report_date string first
                    try:
                        dt = date_parser.parse(report_date, fuzzy=True)
                        date_str = dt.strftime("%Y_%m_%d")
                    except Exception:
                        date_str = datetime.now().strftime("%Y_%m_%d")
                        logger.warning(
                            f"Could not parse date from {report_date}, using current date"
                        )

                    # Download and process the PDF
                    if self._download_pdf(pdf_url, f"{company_code}_{date_str}.pdf"):
                        logger.info(
                            f"Successfully processed PDF for {company_code} dated {date_str}"
                        )
                    else:
                        logger.error(
                            f"Failed to process PDF for {company_code} dated {date_str}"
                        )
                except Exception as e:
                    logger.error(
                        f"Error processing report for {company_code}: {str(e)}"
                    )
                    continue
        except Exception as e:
            logger.error(f"Error scraping data for {company_code}: {str(e)}")
            raise

    def scrape_all_companies(self):
        for company_code in tqdm(self.COMPANIES.keys(), desc="Scraping companies"):
            try:
                self.scrape_company_data(company_code)
            except Exception as e:
                logger.error(f"Failed to scrape {company_code}: {str(e)}")

    def __del__(self):
        if hasattr(self, "driver"):
            self.driver.quit()


def main():
    scraper = CSEScraper()
    scraper.scrape_all_companies()


if __name__ == "__main__":
    main()
