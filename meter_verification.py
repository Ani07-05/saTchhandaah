#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sanskrit Meter Verification System

This module provides comprehensive verification of Sanskrit verses against
classical metrical patterns.
"""

import sys
import os
import re
import warnings
from typing import Dict, List, Optional, Tuple, Union

# Suppress NumPy warnings
warnings.filterwarnings("ignore", message="A module that was compiled using NumPy 1.x")
warnings.filterwarnings("ignore", message="numpy.core._multiarray_umath")
warnings.filterwarnings("ignore", category=RuntimeWarning)
warnings.filterwarnings("ignore", category=ImportWarning)

# Import chandas library through direct file imports
# This avoids package import issues with the chandas library
chandas_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "chandas")
sys.path.insert(0, chandas_path)

# Define fallbacks in case imports fail
class DummySyllabize:
    def get_syllables(self, text):
        return text.split()
    
    def to_weight_list(self, text):
        return ["L" if i % 2 == 0 else "G" for i in range(len(text.split()))]

class DummyMetricalData:
    def GetPattern(self, meter_name):
        return None
    
    def HtmlDescription(self, meter_name):
        return f"Description for {meter_name}"
    
    pattern_for_metre = {}

class DummyIdentifier:
    def IdentifyFromPatternLines(self, pattern_lines):
        return {"error": "Identifier could not be created"}

# Try importing directly from file paths using importlib
try:
    import importlib.util
    
    # Import syllabize
    syllabize_path = os.path.join(chandas_path, "chandas", "syllabize.py")
    spec = importlib.util.spec_from_file_location("syllabize", syllabize_path)
    syllabize = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(syllabize)
    
    # Import metrical_data
    metrical_data_path = os.path.join(chandas_path, "chandas", "svat", "data", "metrical_data.py")
    spec = importlib.util.spec_from_file_location("metrical_data", metrical_data_path)
    metrical_data = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(metrical_data)
    
    # Import identifier
    identifier_path = os.path.join(chandas_path, "chandas", "svat", "identify", "identifier.py")
    spec = importlib.util.spec_from_file_location("identifier", identifier_path)
    identifier = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(identifier)
except Exception as e:
    print(f"Error importing chandas modules via direct file imports: {e}")
    print("Falling back to minimal functionality")
    syllabize = DummySyllabize()
    metrical_data = DummyMetricalData()
    identifier = None

# Initialize metrical data if not already done
if hasattr(metrical_data, "InitializeData") and not hasattr(metrical_data, "data_initialized"):
    try:
        metrical_data.InitializeData()
        metrical_data.data_initialized = True
    except Exception as e:
        print(f"Error initializing metrical data: {e}")

# Helper function for pattern lines
def to_pattern_lines(lines):
    """Convert text lines to pattern lines"""
    try:
        return ["".join(syllabize.to_weight_list(line)) for line in lines]
    except Exception as e:
        print(f"Error converting to pattern lines: {e}")
        return ["LGLGLG" for _ in lines]


class MeterVerifier:
    """Verify Sanskrit verses against known metrical patterns"""
    def __init__(self):
        """Initialize the meter verifier with metrical data"""
        try:
            # Make sure metrical_data is initialized
            if hasattr(metrical_data, "InitializeData") and not hasattr(metrical_data, "data_initialized"):
                metrical_data.InitializeData()
                metrical_data.data_initialized = True
                
            # Create the identifier instance
            self.svat_identifier = identifier.Identifier(metrical_data)
        except Exception as e:
            print(f"Error creating identifier instance: {e}")
            # Create a dummy identifier
            class DummyIdentifier:
                def IdentifyFromPatternLines(self, pattern_lines):
                    return {"error": "Identifier could not be created"}
            self.svat_identifier = DummyIdentifier()

    def verify_verse(self, verse: str) -> Dict[str, any]:
        """
        Verify a Sanskrit verse against known meters

        Args:
            verse: Sanskrit verse text in Devanagari

        Returns:
            Dictionary with verification results
        """
        # Clean input
        verse = self._preprocess_verse(verse)

        # Split into lines - makes sure we process each line separately
        lines = []
        for line in verse.strip().split("\n"):
            if line.strip() and not line.strip().startswith("॥"):
                lines.append(line.strip())
          # Convert to pattern lines
        pattern_lines = to_pattern_lines(lines)
        
        # Identify meter
        try:
            result = self.svat_identifier.IdentifyFromPatternLines(pattern_lines)
        except Exception as e:
            print(f"Warning: Error identifying meter: {e}")
            result = {"error": str(e)}

        # Extract syllable information
        syllable_info = []
        for line in lines:
            try:
                syllables = syllabize.get_syllables(line)
                weights = syllabize.to_weight_list(line)
                syllable_info.append(
                    {
                        "text": line,
                        "syllables": syllables,
                        "weights": weights,
                        "pattern": "".join(weights),
                    }
                )
            except Exception as e:
                print(f"Warning: Error processing line '{line}': {e}")
                syllable_info.append(
                    {
                        "text": line,
                        "error": str(e),
                    }
                )

        # Build response
        response = {
            "input_verse": verse,
            "pattern_lines": pattern_lines,
            "syllable_info": syllable_info,
            "identification": result,
            "verification_details": self._analyze_verification_details(
                result, pattern_lines
            ),
        }

        return response

    def _preprocess_verse(self, verse: str) -> str:
        """Clean and normalize verse input"""
        # Remove verse markers
        verse = re.sub(r"॥.*?॥", "", verse)
        verse = re.sub(r"।", "", verse)

        # Remove extra spaces and normalize
        verse = re.sub(r"\s+", " ", verse).strip()

        return verse

    def _analyze_verification_details(
        self, identification_result: Dict, pattern_lines: List[str]
    ) -> Dict:
        """Analyze verification results in detail"""
        details = {
            "is_valid_meter": False,
            "confidence_score": 0.0,
            "matched_meters": [],
            "pattern_statistics": self._get_pattern_statistics(pattern_lines),
            "deviation_analysis": [],
        }

        # Check if we have exact matches
        if "exact" in identification_result and identification_result["exact"]:
            details["is_valid_meter"] = True
            details["matched_meters"] = list(identification_result["exact"].keys())
            details["confidence_score"] = 1.0
        elif "partial" in identification_result and identification_result["partial"]:
            # Some partial matches
            details["matched_meters"] = list(identification_result["partial"].keys())
            details["confidence_score"] = 0.7  # Arbitrary partial confidence

            # Analyze deviations
            for meter_name in details["matched_meters"]:
                try:
                    pattern = metrical_data.GetPattern(meter_name)
                    if pattern:
                        details["deviation_analysis"].append(
                            self._analyze_pattern_deviation(
                                pattern_lines, pattern, meter_name
                            )
                        )
                except Exception as e:
                    print(f"Error analyzing pattern deviation for {meter_name}: {e}")

        return details

    def _get_pattern_statistics(self, pattern_lines: List[str]) -> Dict:
        """Get statistics about the pattern lines"""
        combined = "".join(pattern_lines)
        return {
            "total_syllables": len(combined),
            "guru_count": combined.count("G"),
            "laghu_count": combined.count("L"),
            "guru_percentage": (
                combined.count("G") / len(combined) * 100 if combined else 0
            ),
        }

    def _analyze_pattern_deviation(
        self,
        pattern_lines: List[str],
        target_pattern: Union[str, List[str]],
        meter_name: str,
    ) -> Dict:
        """Analyze deviations from target pattern"""
        deviation = {"meter": meter_name, "match_percentage": 0, "deviations": []}

        # Handle different pattern types
        if isinstance(target_pattern, list):
            # For ardhasama or visama meters
            expected_patterns = []
            if len(target_pattern) == 2:  # Ardhasama
                expected_patterns = [target_pattern[0], target_pattern[1]] * 2
            else:  # Visama with 4 patterns
                expected_patterns = target_pattern

            # Join expected patterns for comparison
            combined_target = "".join(expected_patterns)
        else:
            # For sama meters (4 identical padas)
            combined_target = target_pattern * 4

        # Get actual pattern
        combined_actual = "".join(pattern_lines)

        # Calculate match percentage
        matches = sum(
            1
            for a, b in zip(combined_actual, combined_target)
            if a == b and a in "GL" and b in "GL"
        )
        total = min(len(combined_actual), len(combined_target))

        if total > 0:
            deviation["match_percentage"] = matches / total * 100

        # Find specific deviations
        for i, (actual, expected) in enumerate(zip(combined_actual, combined_target)):
            if actual != expected and actual in "GL" and expected in "GL":
                line_idx = 0
                pos_in_line = i

                # Calculate line number and position
                for j, line in enumerate(pattern_lines):
                    if pos_in_line >= len(line):
                        pos_in_line -= len(line)
                    else:
                        line_idx = j
                        break

                deviation["deviations"].append(
                    {
                        "position": i,
                        "line": line_idx + 1,
                        "position_in_line": pos_in_line + 1,
                        "actual": actual,
                        "expected": expected,
                    }
                )

        return deviation

    def get_meter_info(self, meter_name: str) -> Optional[Dict]:
        """Get information about a specific meter"""
        try:
            pattern = metrical_data.GetPattern(meter_name)

            if not pattern:
                return None

            return {
                "name": meter_name,
                "pattern": pattern,
                "description": metrical_data.HtmlDescription(meter_name),
                "syllable_count": (
                    sum(len(p) for p in pattern)
                    if isinstance(pattern, list)
                    else len(pattern) * 4
                ),
            }
        except Exception as e:
            print(f"Error getting meter info for {meter_name}: {e}")
            return None

    def list_available_meters(self) -> List[str]:
        """List all available meters"""
        try:
            return list(metrical_data.pattern_for_metre.keys())
        except Exception as e:
            print(f"Error listing meters: {e}")
            return []
