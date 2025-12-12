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

