from io import BytesIO

from pypdf import PdfReader


class PDFExtractionError(ValueError):
    pass


def extract_pdf_text(content: bytes) -> str:
    text, _ = extract_pdf_text_with_metadata(content)
    return text


def extract_pdf_text_with_metadata(content: bytes) -> tuple[str, bool]:
    if not content.startswith(b"%PDF"):
        raise PDFExtractionError("The uploaded file is not a valid PDF.")
    try:
        document = PdfReader(BytesIO(content))
        text = "\n".join(page.extract_text() or "" for page in document.pages).strip()
        used_ocr = False
        if not text:
            text = _ocr_document(document.pages)
            used_ocr = True
    except Exception as exc:
        raise PDFExtractionError("The PDF could not be opened or read.") from exc
    if not text:
        raise PDFExtractionError("The PDF contains no readable text. For scanned/image-only PDFs, install Tesseract OCR and pytesseract.")
    return text, used_ocr


def _ocr_document(pages) -> str:
    try:
        import pytesseract
        from PIL import Image
    except ImportError as exc:
        raise PDFExtractionError("This scanned PDF needs OCR. Install the project dependencies and Tesseract OCR.") from exc
    text_pages = []
    try:
        for page in pages:
            for image_file in page.images:
                image = Image.open(BytesIO(image_file.data)).convert("RGB")
                text_pages.append(pytesseract.image_to_string(image))
    except pytesseract.TesseractNotFoundError as exc:
        raise PDFExtractionError("This scanned PDF needs the Tesseract OCR application. Install Tesseract and add tesseract.exe to PATH.") from exc
    return "\n".join(text_pages).strip()
