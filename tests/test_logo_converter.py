"""Tests for image to ASCII logo conversion."""

import pytest
from PIL import Image

from templates.logo_converter import LogoConversionError, image_to_ascii


def _create_test_image(path: str, color: int = 0):
    image = Image.new("L", (10, 10), color=color)
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


def test_image_to_ascii_rejects_empty_path(tmp_path):
    with pytest.raises(LogoConversionError, match="Image path is required"):
        image_to_ascii("")


def test_image_to_ascii_rejects_nonexistent_file(tmp_path):
    nonexistent_path = tmp_path / "does_not_exist.png"
    
    with pytest.raises(LogoConversionError, match="Image not found"):
        image_to_ascii(str(nonexistent_path))


def test_image_to_ascii_rejects_empty_charset(tmp_path):
    img_path = tmp_path / "logo.png"
    _create_test_image(img_path, color=128)
    
    with pytest.raises(LogoConversionError, match="Character set cannot be empty"):
        image_to_ascii(str(img_path), charset="")


def test_image_to_ascii_aspect_ratio_preserved(tmp_path):
    # Create a tall rectangular image (10x20)
    img_path = tmp_path / "tall_logo.png"
    tall_image = Image.new("L", (10, 20), color=128)
    tall_image.save(img_path)
    
    ascii_art = image_to_ascii(str(img_path), width=10)
    lines = ascii_art.splitlines()
    
    # With aspect ratio 20/10 = 2.0, adjusted by 0.5 factor: height should be ~10
    assert len(lines) > 5  # Should be approximately 10 lines
    assert all(len(line) == 10 for line in lines)


def test_image_to_ascii_character_mapping(tmp_path):
    # Create a black image and a white image to test charset mapping
    black_path = tmp_path / "black.png"
    white_path = tmp_path / "white.png"
    _create_test_image(black_path, color=0)  # Black (darkest)
    _create_test_image(white_path, color=255)  # White (lightest)
    
    charset = "@%#*+=-:. "
    
    black_ascii = image_to_ascii(str(black_path), width=10, charset=charset)
    white_ascii = image_to_ascii(str(white_path), width=10, charset=charset)
    
    # Black image should use darkest char (@), white should use lightest char (space)
    assert "@" in black_ascii
    assert " " in white_ascii
    assert black_ascii.replace("\n", "").replace("@", "") == ""  # All chars are @
    assert white_ascii.replace("\n", "").replace(" ", "") == ""  # All chars are spaces

