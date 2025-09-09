import os
import io
import uuid
from datetime import datetime

from playwright.async_api import async_playwright
from PyPDF2 import PdfReader, PdfWriter


class HtmlToPdfConverter:
    def __init__(self, html_pages: list[str]):
        """
        Initialize the converter with HTML pages and output PDF file name.
        """
        self.html_pages = html_pages
        self.output_folder = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "../../output")
        )

    def create_output_path(self, base_name: str) -> str:
        """
        Creates the folder structure and returns a unique output file path.
        """
        today_date = datetime.today().strftime('%Y-%m-%d')
        day_folder_path = os.path.join(self.output_folder, today_date)
        os.makedirs(day_folder_path, exist_ok=True)

        name, ext = os.path.splitext(base_name)
        unique_suffix = datetime.now().strftime("%H%M%S") + "_" + uuid.uuid4().hex[:6]
        unique_name = f"{name}_{unique_suffix}{ext}"

        return os.path.join(day_folder_path, unique_name)

    async def convert_to_pdf(self, base_name: str = "document.pdf") -> str:
        """Converts the stored HTML pages into a single merged PDF."""
        try:
            pdf_writer = PdfWriter()
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)

                for page_html in self.html_pages:
                    page = await browser.new_page()
                    await page.set_content(page_html)

                    pdf_bytes = await page.pdf(
                        margin={'top': '0', 'left': '0', 'right': '0', 'bottom': '0'}
                    )

                    pdf_reader = PdfReader(io.BytesIO(pdf_bytes))
                    for page_num in range(len(pdf_reader.pages)):
                        pdf_writer.add_page(pdf_reader.pages[page_num])

                    await page.close()

                await browser.close()

            output_pdf_path = self.create_output_path(base_name)
            with open(output_pdf_path, 'wb') as out_file:
                pdf_writer.write(out_file)

            return output_pdf_path

        except Exception as e:
            import traceback
            tb = traceback.format_exc()
            raise RuntimeError(f"Error during conversion: {repr(e)}\nTraceback:\n{tb}")
