"""Extractors convert files/images/documents into text (and metadata).

They are dependency-optional and safe for POC -> prod.
"""

from app.extractors.base import ExtractResult, BaseExtractor
from app.extractors.dispatcher import ExtractorDispatcher

from app.extractors.text_extractor import TextExtractor
from app.extractors.pdf_extractor import PdfExtractor
from app.extractors.docx_extractor import DocxExtractor
from app.extractors.xlsx_extractor import XlsxExtractor
from app.extractors.ocr_extractor import ImageOcrExtractor

__all__ = [
    "ExtractResult",
    "BaseExtractor",
    "ExtractorDispatcher",
    "TextExtractor",
    "PdfExtractor",
    "DocxExtractor",
    "XlsxExtractor",
    "ImageOcrExtractor",
]