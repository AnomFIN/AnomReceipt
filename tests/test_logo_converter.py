"""Tests for image to ASCII logo conversion."""

import pytest
from PIL import Image

from templates.logo_converter import LogoConversionError, image_to_ascii


def _create_test_image(path: str, color: int = 0, width: int = 10, height: int = 10):
    image = Image.new("L", (width, height), color=color)
    image.save(path)


def test_image_to_ascii_success(tmp_path):
    img_path = tmp_path / "logo.png"
    _create_test_image(img_path, color=128)

    ascii_art = image_to_ascii(str(img_path), width=10)
    lines = ascii_art.splitlines()

    assert len(lines) > 0
    assert all(len(line) == 10 for line in lines)


def test_image_to_ascii_invalid_extension(tmp_path):
    bad_path = tmp_path / "logo.txt"
    bad_path.write_text("not an image")

    with pytest.raises(LogoConversionError):
        image_to_ascii(str(bad_path))


def test_image_to_ascii_rejects_bad_width(tmp_path):
    img_path = tmp_path / "logo.jpg"
    _create_test_image(img_path, color=200)

    with pytest.raises(LogoConversionError):
        image_to_ascii(str(img_path), width=0)


def test_image_to_ascii_empty_path():
    """Test that empty image path raises appropriate error."""
    with pytest.raises(LogoConversionError, match="Image path is required"):
        image_to_ascii("")


def test_image_to_ascii_nonexistent_file(tmp_path):
    """Test that non-existent file path raises appropriate error."""
    nonexistent_path = tmp_path / "does_not_exist.png"
    with pytest.raises(LogoConversionError, match="Image not found"):
        image_to_ascii(str(nonexistent_path))


def test_image_to_ascii_empty_charset(tmp_path):
    """Test that empty charset raises appropriate error."""
    img_path = tmp_path / "logo.png"
    _create_test_image(img_path, color=128)
    
    with pytest.raises(LogoConversionError, match="Character set cannot be empty"):
        image_to_ascii(str(img_path), charset="")


def test_image_to_ascii_aspect_ratio_landscape(tmp_path):
    """Test aspect ratio calculation for landscape image."""
    img_path = tmp_path / "landscape.png"
    # Create a wide image (landscape)
    _create_test_image(img_path, color=128, width=100, height=50)
    
    ascii_art = image_to_ascii(str(img_path), width=20)
    lines = ascii_art.splitlines()
    
    # Height should be roughly half of width due to aspect ratio and character height adjustment
    expected_height = int((50 / 100) * 20 * 0.5)
    assert len(lines) == max(1, expected_height)
    assert all(len(line) == 20 for line in lines)


def test_image_to_ascii_aspect_ratio_portrait(tmp_path):
    """Test aspect ratio calculation for portrait image."""
    img_path = tmp_path / "portrait.png"
    # Create a tall image (portrait)
    _create_test_image(img_path, color=128, width=50, height=100)
    
    ascii_art = image_to_ascii(str(img_path), width=10)
    lines = ascii_art.splitlines()
    
    # Height should be roughly twice the width due to aspect ratio and character height adjustment
    expected_height = int((100 / 50) * 10 * 0.5)
    assert len(lines) == max(1, expected_height)
    assert all(len(line) == 10 for line in lines)


def test_image_to_ascii_aspect_ratio_square(tmp_path):
    """Test aspect ratio calculation for square image."""
    img_path = tmp_path / "square.png"
    # Create a square image
    _create_test_image(img_path, color=128, width=100, height=100)
    
    ascii_art = image_to_ascii(str(img_path), width=20)
    lines = ascii_art.splitlines()
    
    # Height should be roughly half of width for square image due to character height adjustment
    expected_height = int((100 / 100) * 20 * 0.5)
    assert len(lines) == max(1, expected_height)
    assert all(len(line) == 20 for line in lines)


def test_image_to_ascii_character_mapping_dark(tmp_path):
    """Test character mapping for very dark image."""
    img_path = tmp_path / "dark.png"
    # Create a very dark image (pixel value = 0 = black)
    _create_test_image(img_path, color=0)
    
    # Use a simple charset where @ is darkest and space is lightest
    charset = "@%#*+=-:. "
    ascii_art = image_to_ascii(str(img_path), width=10, charset=charset)
    
    # Dark pixels should map to the first character(s) in the charset
    assert "@" in ascii_art


def test_image_to_ascii_character_mapping_light(tmp_path):
    """Test character mapping for very light image."""
    img_path = tmp_path / "light.png"
    # Create a very light image (pixel value = 255 = white)
    _create_test_image(img_path, color=255)
    
    # Use a simple charset where @ is darkest and space is lightest
    charset = "@%#*+=-:. "
    ascii_art = image_to_ascii(str(img_path), width=10, charset=charset)
    
    # Light pixels should map to the last character(s) in the charset
    assert " " in ascii_art


def test_image_to_ascii_character_mapping_mid_gray(tmp_path):
    """Test character mapping for mid-gray image."""
    img_path = tmp_path / "gray.png"
    # Create a mid-gray image (pixel value = 128)
    _create_test_image(img_path, color=128)
    
    # Use a simple charset
    charset = "@%#*+=-:. "
    ascii_art = image_to_ascii(str(img_path), width=10, charset=charset)
    
    # Calculate expected character using the same formula as the source code
    pixel_value = 128
    scale = (len(charset) - 1) / 255
    expected_index = int(pixel_value * scale)
    expected_char = charset[expected_index]
    
    # Verify the expected character is in the ASCII art
    assert expected_char in ascii_art

