#!/usr/bin/env python3
"""
Test suite for install.ps1 script functionality.
Tests that the installer works correctly across platforms.
"""

import os
import subprocess
import sys
import unittest
from pathlib import Path


class TestInstallScript(unittest.TestCase):
    """Test the install.ps1 PowerShell installation script."""

    @classmethod
    def setUpClass(cls):
        """Set up test environment."""
        cls.repo_root = Path(__file__).parent.parent
        cls.install_script = cls.repo_root / "install.ps1"
        cls.venv_path = cls.repo_root / "venv"
        cls.log_file = cls.repo_root / "anomreceipt_install.log"

    def tearDown(self):
        """Clean up after each test."""
        # Note: We don't remove venv to avoid re-installing for every test
        # Only remove if explicitly needed
        pass

    def test_install_script_exists(self):
        """Test that install.ps1 exists."""
        self.assertTrue(
            self.install_script.exists(),
            f"install.ps1 should exist at {self.install_script}",
        )

    def test_install_script_is_readable(self):
        """Test that install.ps1 is readable."""
        self.assertTrue(
            os.access(self.install_script, os.R_OK),
            "install.ps1 should be readable",
        )

    def test_pwsh_available(self):
        """Test that PowerShell (pwsh) is available."""
        try:
            result = subprocess.run(
                ["pwsh", "-Version"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            self.assertEqual(
                result.returncode,
                0,
                "pwsh should be available and return version",
            )
        except FileNotFoundError:
            self.skipTest("pwsh (PowerShell Core) is not installed")

    def test_install_script_help(self):
        """Test that install.ps1 -Help works."""
        try:
            result = subprocess.run(
                ["pwsh", "-File", str(self.install_script), "-Help"],
                capture_output=True,
                text=True,
                timeout=10,
                cwd=self.repo_root,
            )
            self.assertEqual(
                result.returncode,
                0,
                "install.ps1 -Help should exit with code 0",
            )
            self.assertIn(
                "AnomReceipt Installer",
                result.stdout,
                "Help output should contain installer name",
            )
            self.assertIn(
                "Platform Support",
                result.stdout,
                "Help should mention platform support",
            )
        except FileNotFoundError:
            self.skipTest("pwsh (PowerShell Core) is not installed")

    def test_install_creates_venv(self):
        """Test that installation creates a virtual environment."""
        # Only run if venv exists (from previous installation)
        if not self.venv_path.exists():
            self.skipTest("venv not created yet - run full installation first")

        # Check for platform-specific venv structure
        if os.name == "nt":  # Windows
            venv_python = self.venv_path / "Scripts" / "python.exe"
            venv_pip = self.venv_path / "Scripts" / "pip.exe"
        else:  # Unix/Linux/macOS
            venv_python = self.venv_path / "bin" / "python"
            venv_pip = self.venv_path / "bin" / "pip"

        self.assertTrue(
            venv_python.exists(),
            f"Virtual environment Python should exist at {venv_python}",
        )
        self.assertTrue(
            venv_pip.exists(),
            f"Virtual environment pip should exist at {venv_pip}",
        )

    def test_install_creates_launch_script(self):
        """Test that installation creates a launch script."""
        if os.name == "nt":  # Windows
            launch_script = self.repo_root / "launch.bat"
        else:  # Unix/Linux/macOS
            launch_script = self.repo_root / "launch.sh"

        # Only test if installation has been run
        if not launch_script.exists():
            self.skipTest(
                "Launch script not created yet - run full installation first"
            )

        self.assertTrue(
            launch_script.exists(),
            f"Launch script should exist at {launch_script}",
        )

        # Check that it's executable on Unix
        if os.name != "nt":
            self.assertTrue(
                os.access(launch_script, os.X_OK),
                "Launch script should be executable on Unix systems",
            )

    def test_install_creates_log(self):
        """Test that installation creates a log file."""
        # Only test if installation has been run
        if not self.log_file.exists():
            self.skipTest("Log file not created yet - run full installation first")

        self.assertTrue(
            self.log_file.exists(),
            f"Installation log should exist at {self.log_file}",
        )

        # Check log contains expected content
        with open(self.log_file, "r") as f:
            log_content = f.read()

        self.assertIn(
            "Starting installation",
            log_content,
            "Log should contain installation start message",
        )
        self.assertIn(
            "PowerShell version",
            log_content,
            "Log should contain PowerShell version",
        )
        self.assertIn(
            "Platform:",
            log_content,
            "Log should contain platform information",
        )

    def test_requirements_installed(self):
        """Test that all requirements are installed in venv."""
        if not self.venv_path.exists():
            self.skipTest("venv not created yet - run full installation first")

        # Get venv python
        if os.name == "nt":
            venv_python = str(self.venv_path / "Scripts" / "python.exe")
        else:
            venv_python = str(self.venv_path / "bin" / "python")

        # Test importing key packages
        test_packages = [
            "PySide6",
            "yaml",
            "escpos",
            "PIL",
            "requests",
            "pytesseract",
            "cv2",
            "numpy",
        ]

        for package in test_packages:
            result = subprocess.run(
                [venv_python, "-c", f"import {package}"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            self.assertEqual(
                result.returncode,
                0,
                f"Package {package} should be importable in venv",
            )


class TestInstallScriptPlatformDetection(unittest.TestCase):
    """Test platform detection in install.ps1."""

    @classmethod
    def setUpClass(cls):
        """Set up test environment."""
        cls.repo_root = Path(__file__).parent.parent
        cls.install_script = cls.repo_root / "install.ps1"

    def test_script_contains_platform_detection(self):
        """Test that script contains platform detection code."""
        with open(self.install_script, "r") as f:
            script_content = f.read()

        self.assertIn(
            "$IsWindowsPlatform",
            script_content,
            "Script should contain platform detection variable",
        )
        self.assertIn(
            "$VenvScriptsDir",
            script_content,
            "Script should contain venv scripts directory variable",
        )
        self.assertIn(
            "Platform:",
            script_content,
            "Script should log platform information",
        )

    def test_script_supports_both_platforms(self):
        """Test that script has logic for both Windows and Unix."""
        with open(self.install_script, "r") as f:
            script_content = f.read()

        # Check for Windows-specific paths
        self.assertIn(
            '"Scripts"',
            script_content,
            "Script should reference Windows Scripts directory",
        )

        # Check for Unix-specific paths
        self.assertIn(
            '"bin"',
            script_content,
            "Script should reference Unix bin directory",
        )

        # Check for both launch script types
        self.assertIn(
            "launch.bat",
            script_content,
            "Script should create launch.bat for Windows",
        )
        self.assertIn(
            "launch.sh",
            script_content,
            "Script should create launch.sh for Unix",
        )


def run_tests():
    """Run all tests."""
    # Discover and run tests
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(sys.modules[__name__])
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(run_tests())
