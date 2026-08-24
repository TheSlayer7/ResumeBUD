import fitz


class PDFExtractionError(ValueError):
    pass


def extract_pdf_text(content: bytes) -> str:
    text, _ = extract_pdf_text_with_metadata(content)
    return text


def extract_pdf_text_with_metadata(content: bytes) -> tuple[str, bool]:
    if not content.startswith(b"%PDF"):
        raise PDFExtractionError("The uploaded file is not a valid PDF.")
    try:
        with fitz.open(stream=content, filetype="pdf") as document:
            text = "\n".join(page.get_text() for page in document).strip()
            used_ocr = False
            if not text:
                text = _ocr_document(document)
                used_ocr = True
    except Exception as exc:
        raise PDFExtractionError("The PDF could not be opened or read.") from exc
    if not text:
        raise PDFExtractionError("The PDF contains no readable text. For scanned/image-only PDFs, install Tesseract OCR and pytesseract.")
    return text, used_ocr


def _ocr_document(document) -> str:
    try:
        import pytesseract
        from PIL import Image
    except ImportError as exc:
        raise PDFExtractionError("This scanned PDF needs OCR. Install the project dependencies and Tesseract OCR.") from exc
    pages = []
    try:
        for page in document:
            pixmap = page.get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False)
            image = Image.frombytes("RGB", [pixmap.width, pixmap.height], pixmap.samples)
            pages.append(pytesseract.image_to_string(image))
    except pytesseract.TesseractNotFoundError as exc:
        raise PDFExtractionError("This scanned PDF needs the Tesseract OCR application. Install Tesseract and add tesseract.exe to PATH.") from exc
    return "\n".join(pages).strip()
