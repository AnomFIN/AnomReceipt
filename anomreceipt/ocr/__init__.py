"""
OCR module for AnomReceipt.
Handles image-to-text conversion for receipts with structure preservation.
"""

from .ocr_engine import OCREngine, OCRResult

__all__ = ['OCREngine', 'OCRResult']
