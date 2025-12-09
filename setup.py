#!/usr/bin/env python3
"""
Setup script for AnomReceipt
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="anomreceipt",
    version="1.0.0",
    author="AnomFIN",
    description="Receipt printing application for Epson TM-T70II (ESC/POS) printers",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/AnomFIN/AnomReceipt",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Office/Business :: Financial :: Point-Of-Sale",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Operating System :: POSIX :: Linux",
    ],
    python_requires=">=3.7",
    install_requires=[
        "PyQt5>=5.15.0",
        "PyYAML>=6.0",
        "python-escpos>=3.0",
        "pillow>=10.3.0",
    ],
    entry_points={
        "console_scripts": [
            "anomreceipt=main:main",
        ],
    },
    include_package_data=True,
)
