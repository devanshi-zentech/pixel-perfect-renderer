import io
from pypdf import PdfReader, PdfWriter

from app.core.browser_manager import browser_manager
from app.core import constants


class HtmlToPdfConverter:
    def __init__(self, pages_data: list[dict]):
        """
        Initialize the converter with HTML pages and their dimensions.
        :param pages_data: List of dictionaries, each containing 'html', 'width', and 'height' keys.
        """
        self.pages_data = pages_data

    def _is_blank_page(self, pdf_page) -> bool:
        """
        Check if a PDF page is blank (no text and minimal content stream).
        
        :param pdf_page: A page object from PdfReader.
        :return: True if the page is blank, False otherwise.
        """
        # Check extracted text
        text = pdf_page.extract_text() or ""
        if text.strip():
            return False

        # Check raw content stream size
        content = pdf_page.get_contents()
        if not content:
            return True

        if isinstance(content, list):
            total_size = sum(len(c.get_data()) for c in content)
        else:
            total_size = len(content.get_data())

        return total_size < 20  # very tiny streams usually mean blank page

    async def convert_to_pdf(self) -> str:
        """
        Converts the stored HTML pages into a single merged PDF, skipping blank pages.
        :return: PDF Bytes.
        """
        try:
            pdf_writer = PdfWriter()
            browser = await browser_manager.get_browser()

            for page_data in self.pages_data:
                page = await browser.new_page()
                await page.set_content(page_data["html"])

                pdf_bytes = await page.pdf(
                    width=f'{page_data["width"]}px',
                    height=f'{page_data["height"]}px',
                    margin={'top': '0', 'left': '0', 'right': '0', 'bottom': '0'}
                )

                pdf_reader = PdfReader(io.BytesIO(pdf_bytes))
                for pdf_page in pdf_reader.pages:
                    if not self._is_blank_page(pdf_page):
                        pdf_writer.add_page(pdf_page)

                await page.close()

            output_stream = io.BytesIO()
            pdf_writer.write(output_stream)
            output_stream.seek(0)

            return output_stream.getvalue()

        except Exception as e:
            import traceback
            tb = traceback.format_exc()
            raise RuntimeError(f"Error during conversion: {repr(e)}\nTraceback:\n{tb}")
