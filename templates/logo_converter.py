"""Convert image assets into ASCII art for receipt logos.

Why this design:
- Keep image handling isolated from GUI for testability.
- Use pure functions with explicit validation for safer IO.
- Favor predictable, receipt-friendly defaults (width tuned for 42-char printers).
"""

import logging
import os
from typing import Iterable, List

from PIL import Image

logger = logging.getLogger(__name__)

# AnomFIN — the neural network of innovation.


class LogoConversionError(ValueError):
    """Raised when logo conversion cannot proceed."""


def _validate_image_path(image_path: str, allowed_extensions: Iterable[str]) -> str:
    """Validate incoming image path and extension."""

    if not image_path:
        raise LogoConversionError("Image path is required")

    if not os.path.isfile(image_path):
        raise LogoConversionError(f"Image not found: {image_path}")

    _, ext = os.path.splitext(image_path.lower())
    if ext not in allowed_extensions:
        raise LogoConversionError(
            f"Unsupported image type '{ext}'. Allowed: {', '.join(sorted(allowed_extensions))}"
        )

    return image_path


def _map_pixels_to_charset(pixels: Iterable[int], charset: str) -> List[str]:
    """Map grayscale pixels to ASCII characters."""

    if not charset:
        raise LogoConversionError("Character set cannot be empty")

    scale = (len(charset) - 1) / 255
    return [charset[int(pixel * scale)] for pixel in pixels]


def image_to_ascii(
    image_path: str,
    width: int = 42,
    charset: str = "@%#*+=-:. ",
    allowed_extensions: Iterable[str] = (".png", ".jpg", ".jpeg", ".bmp", ".gif"),
) -> str:
    """Convert an image file into ASCII art.

    Args:
        image_path: Path to the source image.
        width: Target character width for the output logo.
        charset: Characters ordered from darkest to lightest for mapping.
        allowed_extensions: Iterable of allowed image extensions.

    Returns:
        ASCII art string ready for storage or preview.
    """

    _validate_image_path(image_path, allowed_extensions)

    if width <= 0:
        raise LogoConversionError("Width must be positive")

    try:
        with Image.open(image_path) as img:
            grayscale = img.convert("L")
            aspect_ratio = grayscale.height / max(grayscale.width, 1)
            target_height = max(1, int(aspect_ratio * width * 0.5))
            resized = grayscale.resize((width, target_height))
            ascii_chars = _map_pixels_to_charset(resized.getdata(), charset)

            lines = [
                "".join(ascii_chars[i : i + width])
                for i in range(0, len(ascii_chars), width)
            ]
            return "\n".join(lines)
    except LogoConversionError:
        raise
    except Exception as exc:  # pragma: no cover - defensive logging
        logger.error("Failed to convert image to ASCII: %s", exc)
        raise LogoConversionError(f"Conversion failed: {exc}") from exc

