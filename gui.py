#!/usr/bin/env python3
"""
AnomReceipt - GUI Entry Point
Alternative entry point for launching the receipt printer GUI
"""

import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Import and run main
from main import main

if __name__ == '__main__':
    sys.exit(main())
