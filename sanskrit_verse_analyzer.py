#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sanskrit Verse Analyzer

A beautiful and user-friendly CLI tool to analyze Sanskrit verses and identify their meter patterns.
"""
import os
import sys
import time
import re
import json
import codecs
import argparse
import warnings
import importlib.util
from typing import Dict, List, Optional, Union

# Add chandas to path and ensure UTF-8 encoding
chandas_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "chandas")
if chandas_path not in sys.path:
    sys.path.insert(0, chandas_path)

# Patch JSON load for UTF-8 support
original_json_load = json.load


def utf8_json_load(file_obj, *args, **kwargs):
    """UTF-8 wrapper for JSON loading"""
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

# Suppress warnings
warnings.filterwarnings("ignore", message="A module that was compiled using NumPy 1.x")
warnings.filterwarnings("ignore", message="numpy.core._multiarray_umath")
warnings.filterwarnings("ignore", category=RuntimeWarning)
warnings.filterwarnings("ignore", category=ImportWarning)


# CLI formatting utilities
class Colors:
    HEADER = "\033[95m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"
    END = "\033[0m"


def print_header(text):
    """Print a formatted header"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'=' * 60}{Colors.END}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text.center(60)}{Colors.END}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'=' * 60}{Colors.END}\n")


def print_section(text):
    """Print a section header"""
    print(f"\n{Colors.BLUE}{Colors.BOLD}{text}{Colors.END}")
    print(f"{Colors.BLUE}{'-' * len(text)}{Colors.END}")


def print_success(text):
    """Print a success message"""
    print(f"{Colors.GREEN}{text}{Colors.END}")


def print_warning(text):
    """Print a warning message"""
    print(f"{Colors.YELLOW}{text}{Colors.END}")


def print_error(text):
    """Print an error message"""
    print(f"{Colors.RED}{text}{Colors.END}")


def print_info(text):
    """Print highlighted info"""
    print(f"{Colors.CYAN}{text}{Colors.END}")


def animate_loading(duration=1.0, text="Analyzing"):
    """Show an animated loading indicator"""
    chars = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"
    delay = 0.1
    iterations = int(duration / delay)

    for i in range(iterations):
        char = chars[i % len(chars)]
        sys.stdout.write(f"\r{text} {char}")
        sys.stdout.flush()
        time.sleep(delay)
    sys.stdout.write("\r" + " " * (len(text) + 2) + "\r")
    sys.stdout.flush()


class SanskritVerseAnalyzer:
    """Analyze Sanskrit verses and identify their metrical patterns"""

    def __init__(self):
        """Initialize the analyzer"""
        try:
            # Import modules directly from file paths
            self.initialized = True

            # Import syllabize
            syllabize_path = os.path.join(chandas_path, "chandas", "syllabize.py")
            spec = importlib.util.spec_from_file_location("syllabize", syllabize_path)
            self.syllabize = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(self.syllabize)

            # Import metrical_data
            metrical_data_path = os.path.join(
                chandas_path, "chandas", "svat", "data", "metrical_data.py"
            )
            spec = importlib.util.spec_from_file_location(
                "metrical_data", metrical_data_path
            )
            self.metrical_data = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(self.metrical_data)

            # Initialize metrical data
            if not hasattr(self.metrical_data, "data_initialized"):
                self.metrical_data.InitializeData()
                self.metrical_data.data_initialized = True

            # Import identifier
            identifier_path = os.path.join(
                chandas_path, "chandas", "svat", "identify", "identifier.py"
            )
            spec = importlib.util.spec_from_file_location("identifier", identifier_path)
            identifier = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(identifier)

            # Create identifier instance
            self.identifier = identifier.Identifier(self.metrical_data)

            print_success("Sanskrit Verse Analyzer initialized successfully!")
        except Exception as e:
            print_error(f"Error initializing analyzer: {e}")
            self.initialized = False

    def analyze_verse(self, verse: str) -> Dict:
        """Analyze a Sanskrit verse"""
        if not self.initialized:
            return {"error": "Analyzer not properly initialized"}

        try:
            # Clean the verse
            verse = self._preprocess_verse(verse)

            # Split into lines
            lines = [
                line.strip()
                for line in verse.strip().split("\n")
                if line.strip() and not line.strip().startswith("॥")
            ]

            # Get syllables and patterns for each line
            syllable_info = []
            pattern_lines = []

            for line in lines:
                syllables = self.syllabize.get_syllables(line)
                weights = self.syllabize.to_weight_list(line)
                pattern = "".join(weights)

                syllable_info.append(
                    {
                        "text": line,
                        "syllables": syllables,
                        "weights": weights,
                        "pattern": pattern,
                    }
                )

                pattern_lines.append(pattern)

            # Calculate pattern statistics
            combined_pattern = "".join(pattern_lines)
            pattern_statistics = {
                "total_syllables": len(combined_pattern),
                "guru_count": combined_pattern.count("G"),
                "laghu_count": combined_pattern.count("L"),
                "guru_percentage": (
                    combined_pattern.count("G") / len(combined_pattern) * 100
                    if combined_pattern
                    else 0
                ),
            }

            # Identify meter
            identification = self.identifier.IdentifyFromPatternLines(pattern_lines)

            # Extract matched meters
            matched_meters = []
            is_valid_meter = False
            confidence_score = 0

            if "exact" in identification and identification["exact"]:
                matched_meters = list(identification["exact"].keys())
                is_valid_meter = True
                confidence_score = 100
            elif "partial" in identification and identification["partial"]:
                matched_meters = list(identification["partial"].keys())
                confidence_score = 70  # Default partial confidence

            # Build response
            result = {
                "input_verse": verse,
                "lines": lines,
                "syllable_info": syllable_info,
                "pattern_lines": pattern_lines,
                "identification": identification,
                "verification_details": {
                    "is_valid_meter": is_valid_meter,
                    "matched_meters": matched_meters,
                    "confidence_score": confidence_score,
                    "pattern_statistics": pattern_statistics,
                },
            }

            return result

        except Exception as e:
            return {"error": str(e)}

    def _preprocess_verse(self, verse: str) -> str:
        """Clean and normalize verse input"""
        # Remove verse markers
        verse = re.sub(r"॥.*?॥", "", verse)
        verse = re.sub(r"।", "", verse)

        # Remove extra spaces and normalize
        verse = re.sub(r"\s+", " ", verse).strip()

        return verse

    def display_results(self, results: Dict) -> None:
        """Display analysis results in a beautiful format"""
        if "error" in results:
            print_error(f"Error analyzing verse: {results['error']}")
            return

        # Verse input
        print_section("Input Verse")
        print(results.get("input_verse", ""))

        # Syllable breakdown
        print_section("Syllable Breakdown")
        for i, line_info in enumerate(results.get("syllable_info", []), 1):
            print(f"Line {i}: {line_info['text']}")
            print(
                f"  Syllables ({len(line_info['syllables'])}): {Colors.BOLD}{', '.join(line_info['syllables'])}{Colors.END}"
            )
            print(f"  Pattern: {Colors.CYAN}{line_info['pattern']}{Colors.END}")
            print()

        # Pattern statistics
        stats = results.get("verification_details", {}).get("pattern_statistics", {})
        print_section("Metrical Statistics")
        print(
            f"Total syllables: {Colors.BOLD}{stats.get('total_syllables', 0)}{Colors.END}"
        )
        print(
            f"Guru (heavy) syllables: {Colors.BOLD}{stats.get('guru_count', 0)}{Colors.END}"
        )
        print(
            f"Laghu (light) syllables: {Colors.BOLD}{stats.get('laghu_count', 0)}{Colors.END}"
        )
        print(
            f"Guru percentage: {Colors.BOLD}{stats.get('guru_percentage', 0):.2f}%{Colors.END}"
        )

        # Meter identification
        print_section("Meter Identification")
        verification = results.get("verification_details", {})
        if verification.get("is_valid_meter", False):
            meters = verification.get("matched_meters", [])
            print_success(
                f"Valid meter detected: {Colors.BOLD}{', '.join(meters)}{Colors.END}"
            )
            print_success(f"Confidence: {Colors.BOLD}100%{Colors.END}")
        elif verification.get("matched_meters", []):
            meters = verification.get("matched_meters", [])
            print_warning(
                f"Partial match: {Colors.BOLD}{', '.join(meters)}{Colors.END}"
            )
            print_warning(
                f"Confidence: {Colors.BOLD}{verification.get('confidence_score', 0):.2f}%{Colors.END}"
            )
        else:
            print_warning("No known meter matched")


def main():
    """Main function to run the analyzer"""
    parser = argparse.ArgumentParser(description="Sanskrit Verse Analyzer")
    parser.add_argument(
        "-f", "--file", help="Path to a file containing a Sanskrit verse"
    )
    parser.add_argument("-v", "--verse", help="Sanskrit verse text")
    args = parser.parse_args()

    print_header("Sanskrit Verse Analyzer")

    # Initialize analyzer
    analyzer = SanskritVerseAnalyzer()

    # Get verse input
    verse = ""
    if args.file:
        try:
            with open(args.file, "r", encoding="utf-8") as f:
                verse = f.read()
            print(f"Reading verse from file: {args.file}")
        except Exception as e:
            print_error(f"Error reading file: {e}")
            return
    elif args.verse:
        verse = args.verse
    else:
        print("Enter your Sanskrit verse below (enter a blank line when finished):")
        print()

        # Read input verse until user enters a blank line
        lines = []
        while True:
            line = input()
            if not line.strip():  # Empty line signals end of input
                break
            lines.append(line)

        verse = "\n".join(lines)

    if not verse.strip():
        print_warning("No verse provided. Using a sample verse instead.")
        verse = """वागर्थाविव संपृक्तौ वागर्थप्रतिपत्तये।
जगतः पितरौ वन्दे पार्वतीपरमेश्वरौ॥"""
        print(verse)

    # Show loading animation
    print("\nProcessing your verse...")
    animate_loading(1.5, "Analyzing metrical patterns")

    # Analyze verse
    results = analyzer.analyze_verse(verse)

    # Display results
    analyzer.display_results(results)

    print("\nThank you for using Sanskrit Verse Analyzer!")


if __name__ == "__main__":
    main()
