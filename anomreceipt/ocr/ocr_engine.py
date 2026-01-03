"""
OCR Engine for receipt processing.
Provides high-quality text extraction with structure preservation.
"""

import cv2
import numpy as np
import pytesseract
from PIL import Image
from pathlib import Path
from typing import Optional, Tuple
from dataclasses import dataclass
from ..core import get_logger, with_error_handling

logger = get_logger(__name__)


@dataclass
class OCRResult:
    """Result from OCR processing."""
    text: str
    confidence: float
    structured_text: str
    has_logo: bool
    image_processed: bool


class OCREngine:
    """
    Advanced OCR engine for receipt processing.
    Handles various fonts, sizes, and layouts with structure preservation.
    """
    
    # Image preprocessing constants
    ADAPTIVE_THRESHOLD_BLOCK_SIZE = 11
    ADAPTIVE_THRESHOLD_C = 2
    
    def __init__(self):
        """Initialize OCR engine."""
        self.tesseract_available = self._check_tesseract()
        logger.info(f"OCR Engine initialized (Tesseract available: {self.tesseract_available})")
    
    @staticmethod
    def _check_tesseract() -> bool:
        """Check if Tesseract is available."""
        try:
            pytesseract.get_tesseract_version()
            return True
        except Exception as e:
            logger.warning(f"Tesseract not available: {e}")
            return False
    
    @with_error_handling(
        error_title="OCR Processing Failed",
        error_message="Failed to process the image",
        default_return=None
    )
    def process_image(
        self,
        image_path: str,
        enhance: bool = True
    ) -> Optional[OCRResult]:
        """
        Process an image and extract text.
        
        Args:
            image_path: Path to image file
            enhance: Whether to enhance image before OCR
        
        Returns:
            OCR result or None on failure
        """
        if not self.tesseract_available:
            logger.error("Tesseract is not available")
            return OCRResult(
                text="Tesseract OCR is not installed.\n\n"
                     "Please install Tesseract to use OCR features:\n"
                     "https://github.com/UB-Mannheim/tesseract/wiki",
                confidence=0.0,
                structured_text="",
                has_logo=False,
                image_processed=False
            )
        
        logger.info(f"Processing image: {image_path}")
        
        # Load image
        image = self._load_image(image_path)
        if image is None:
            return None
        
        # Preprocess image
        if enhance:
            image = self._preprocess_image(image)
        
        # Detect logo region
        has_logo = self._detect_logo_region(image)
        
        # Perform OCR
        text, confidence = self._perform_ocr(image)
        
        # Structure the text
        structured_text = self._structure_text(text)
        
        logger.info(f"OCR completed with confidence: {confidence:.2f}%")
        
        return OCRResult(
            text=text,
            confidence=confidence,
            structured_text=structured_text,
            has_logo=has_logo,
            image_processed=True
        )
    
    def _load_image(self, image_path: str) -> Optional[np.ndarray]:
        """Load image from file."""
        try:
            img_path = Path(image_path)
            if not img_path.exists():
                logger.error(f"Image file not found: {image_path}")
                return None
            
            # Read image with OpenCV
            image = cv2.imread(str(img_path))
            
            if image is None:
                logger.error(f"Failed to load image: {image_path}")
                return None
            
            logger.info(f"Image loaded: {image.shape}")
            return image
        
        except Exception as e:
            logger.error(f"Error loading image: {e}", exc_info=True)
            return None
    
    def _preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """
        Preprocess image for better OCR accuracy.
        
        Args:
            image: Input image
        
        Returns:
            Preprocessed image
        """
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Denoise
            denoised = cv2.fastNlMeansDenoising(gray)
            
            # Increase contrast
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            enhanced = clahe.apply(denoised)
            
            # Binarization with adaptive thresholding
            binary = cv2.adaptiveThreshold(
                enhanced,
                255,
                cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                cv2.THRESH_BINARY,
                self.ADAPTIVE_THRESHOLD_BLOCK_SIZE,
                self.ADAPTIVE_THRESHOLD_C
            )
            
            # Morphological operations to clean up
            kernel = np.ones((3, 3), np.uint8)
            cleaned = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
            
            logger.debug("Image preprocessing completed")
            return cleaned
        
        except Exception as e:
            logger.warning(f"Error preprocessing image: {e}")
            return image
    
    def _detect_logo_region(self, image: np.ndarray) -> bool:
        """
        Detect if image contains a logo.
        
        Args:
            image: Input image
        
        Returns:
            True if logo detected
        """
        try:
            # Convert to grayscale if needed
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                gray = image
            
            # Detect edges
            edges = cv2.Canny(gray, 50, 150)
            
            # Find contours
            contours, _ = cv2.findContours(
                edges,
                cv2.RETR_EXTERNAL,
                cv2.CHAIN_APPROX_SIMPLE
            )
            
            # Check for large contours (potential logos)
            height, width = gray.shape
            min_area = (height * width) * 0.05  # At least 5% of image
            
            for contour in contours:
                area = cv2.contourArea(contour)
                if area > min_area:
                    logger.info("Logo region detected")
                    return True
            
            return False
        
        except Exception as e:
            logger.warning(f"Error detecting logo: {e}")
            return False
    
    def _perform_ocr(self, image: np.ndarray) -> Tuple[str, float]:
        """
        Perform OCR on image.
        
        Args:
            image: Preprocessed image
        
        Returns:
            Tuple of (extracted text, confidence percentage)
        """
        try:
            # Convert to PIL Image
            if len(image.shape) == 2:
                pil_image = Image.fromarray(image)
            else:
                pil_image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
            
            # Configure Tesseract for better receipt reading
            # PSM 6 = Assume a single uniform block of text
            # PSM 4 = Assume a single column of text of variable sizes
            custom_config = r'--oem 3 --psm 4'
            
            # Perform OCR with detailed data to preserve line structure
            data = pytesseract.image_to_data(
                pil_image,
                config=custom_config,
                output_type=pytesseract.Output.DICT
            )
            
            # Build text preserving line structure
            lines = {}
            confidences = []
            
            for i in range(len(data['text'])):
                conf = data['conf'][i]
                text = data['text'][i].strip()
                
                if conf > 0 and text:  # Valid detection
                    block_num = data['block_num'][i]
                    par_num = data['par_num'][i]
                    line_num = data['line_num'][i]
                    
                    # Create unique line key
                    line_key = (block_num, par_num, line_num)
                    
                    if line_key not in lines:
                        lines[line_key] = []
                    
                    lines[line_key].append(text)
                    confidences.append(float(conf))
            
            # Join words within lines and lines with newlines
            line_texts = []
            for line_key in sorted(lines.keys()):
                line_text = ' '.join(lines[line_key])
                line_texts.append(line_text)
            
            full_text = '\n'.join(line_texts)
            
            # Calculate average confidence
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
            
            logger.debug(f"OCR extracted {len(line_texts)} lines with {len(confidences)} words")
            return full_text, avg_confidence
        
        except Exception as e:
            logger.error(f"Error performing OCR: {e}", exc_info=True)
            return "", 0.0
    
    def _structure_text(self, text: str) -> str:
        """
        Structure and format extracted text to look human-formatted.
        The input text already has line breaks preserved from OCR.
        
        Args:
            text: Raw OCR text with line breaks
        
        Returns:
            Structured and formatted text
        """
        try:
            # Text already has line structure from OCR, just clean it up
            lines = text.split('\n')
            structured = []
            
            for line in lines:
                line = line.strip()
                if not line:
                    # Preserve empty lines for spacing
                    structured.append('')
                    continue
                
                # Keep the line as-is since OCR already provides reasonable structure
                # Just ensure it's not too long (wrap if needed)
                line_width = 80  # Wider for receipt viewing
                
                if len(line) <= line_width:
                    structured.append(line)
                else:
                    # Wrap long lines
                    words = line.split()
                    current_line = []
                    for word in words:
                        test_line = ' '.join(current_line + [word])
                        if len(test_line) <= line_width:
                            current_line.append(word)
                        else:
                            if current_line:
                                structured.append(' '.join(current_line))
                            current_line = [word]
                    if current_line:
                        structured.append(' '.join(current_line))
            
            # Join with newlines
            result = '\n'.join(structured)
            
            logger.debug("Text structured successfully")
            return result
        
        except Exception as e:
            logger.warning(f"Error structuring text: {e}")
            return text
    
    @with_error_handling(
        error_title="Image Enhancement Failed",
        error_message="Failed to enhance the image",
        default_return=None
    )
    def enhance_receipt_image(
        self,
        image_path: str,
        output_path: Optional[str] = None
    ) -> Optional[str]:
        """
        Enhance a receipt image for better readability.
        
        Args:
            image_path: Path to input image
            output_path: Path to save enhanced image (optional)
        
        Returns:
            Path to enhanced image or None on failure
        """
        logger.info(f"Enhancing image: {image_path}")
        
        # Load image
        image = self._load_image(image_path)
        if image is None:
            return None
        
        # Enhance
        enhanced = self._preprocess_image(image)
        
        # Determine output path
        if output_path is None:
            img_path = Path(image_path)
            output_path = str(img_path.parent / f"{img_path.stem}_enhanced{img_path.suffix}")
        
        # Save enhanced image
        try:
            cv2.imwrite(output_path, enhanced)
            logger.info(f"Enhanced image saved: {output_path}")
            return output_path
        except Exception as e:
            logger.error(f"Failed to save enhanced image: {e}")
            return None
