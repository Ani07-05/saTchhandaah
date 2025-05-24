#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sanskrit Verse Analyzer - Easy Launch Script

This script sets up the necessary environment and launches the Sanskrit Verse Analyzer.
Just run this script and paste your Sanskrit verse - press Enter on a blank line to analyze.
"""

import os
import sys
import json
import codecs
import warnings
import importlib.util
import subprocess

# Suppress warnings
warnings.filterwarnings("ignore", message="A module that was compiled using NumPy 1.x")
warnings.filterwarnings("ignore", message="numpy.core._multiarray_umath")
warnings.filterwarnings("ignore", category=RuntimeWarning)
warnings.filterwarnings("ignore", category=ImportWarning)


def setup_environment():
    """Setup the environment before running the analyzer"""
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Add chandas to path
    chandas_path = os.path.join(script_dir, "chandas")
    if chandas_path not in sys.path:
        sys.path.insert(0, chandas_path)

    # Patch JSON load for UTF-8 support
    original_json_load = json.load

    def utf8_json_load(file_obj, *args, **kwargs):
        if isinstance(file_obj, codecs.StreamReader):
            return original_json_load(file_obj, *args, **kwargs)
        try:
            file_path = file_obj.name
            file_obj.close()
            with codecs.open(file_path, "r", encoding="utf-8") as f:
                return original_json_load(f, *args, **kwargs)
        except Exception:
            return original_json_load(file_obj, *args, **kwargs)

    json.load = utf8_json_load

    return True


def main():
    """Main function"""
    print("Setting up environment...")
    setup_environment()

    # Launch the analyzer
    try:
        from sanskrit_verse_analyzer import main as run_analyzer

        run_analyzer()
    except ImportError:
        print("Error: Could not import the Sanskrit Verse Analyzer.")
        print("Make sure the sanskrit_verse_analyzer.py file is in the same directory.")
        sys.exit(1)


if __name__ == "__main__":
    main()
