#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cleanup Script for Sanskrit Meter Verification System

This script removes unnecessary files and keeps only the essential ones
for the Sanskrit meter verification system.
"""

import os
import sys
import shutil
from pathlib import Path

# Files to keep (essential files)
ESSENTIAL_FILES = [
    "meter_verification.py",
    "sanskrit_verse_analyzer.py",
    "analyze.py",
    "requirements.txt",
    "setup_env_before_run.py",
    "README.md",
    "analyze_custom_verse.py",
]

# Directories to keep
ESSENTIAL_DIRS = [
    "chandas",
]


def clean_directory():
    """Clean the current directory by removing unnecessary files"""
    script_dir = os.path.dirname(os.path.abspath(__file__))

    print(f"Cleaning directory: {script_dir}")
    print("=" * 60)

    # List all files in the directory
    all_files = []
    for entry in os.scandir(script_dir):
        if entry.is_file():
            if (
                entry.name not in ESSENTIAL_FILES
                and not entry.name.startswith(".")
                and entry.name != "cleanup.py"
            ):
                all_files.append(entry.name)

    # List all directories that are not essential
    all_dirs = []
    for entry in os.scandir(script_dir):
        if entry.is_dir():
            if entry.name not in ESSENTIAL_DIRS and not entry.name.startswith("."):
                all_dirs.append(entry.name)

    # Ask for confirmation
    print("The following files will be removed:")
    for file in all_files:
        print(f"- {file}")

    print("\nThe following directories will be removed:")
    for directory in all_dirs:
        print(f"- {directory}")

    confirmation = input("\nAre you sure you want to remove these files? (y/N): ")

    if confirmation.lower() != "y":
        print("Operation cancelled.")
        return

    # Remove files
    removed_files = 0
    failed_files = 0
    for file in all_files:
        try:
            os.remove(os.path.join(script_dir, file))
            print(f"Removed: {file}")
            removed_files += 1
        except Exception as e:
            print(f"Error removing {file}: {e}")
            failed_files += 1

    # Remove directories
    removed_dirs = 0
    failed_dirs = 0
    for directory in all_dirs:
        try:
            shutil.rmtree(os.path.join(script_dir, directory))
            print(f"Removed directory: {directory}")
            removed_dirs += 1
        except Exception as e:
            print(f"Error removing directory {directory}: {e}")
            failed_dirs += 1

    print("\nCleanup Summary:")
    print(f"- Removed files: {removed_files}")
    print(f"- Failed files: {failed_files}")
    print(f"- Removed directories: {removed_dirs}")
    print(f"- Failed directories: {failed_dirs}")

    print("\nKeeping essential files:")
    for file in ESSENTIAL_FILES:
        if os.path.exists(os.path.join(script_dir, file)):
            print(f"- {file}")
        else:
            print(f"- {file} (missing)")


if __name__ == "__main__":
    clean_directory()
