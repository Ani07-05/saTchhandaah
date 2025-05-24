#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import setup_env_before_run
import sys
import os


def analyze_verse():
    print("Enter your Sanskrit verse (enter a blank line when finished):")

    # Read multiple lines from stdin until a blank line
    lines = []
    while True:
        line = input()
        if not line.strip():  # Empty line signals end of input
            break
        lines.append(line)

    verse = "\n".join(lines)

    if not verse.strip():
        print("No verse entered.")
        return

    try:
        from meter_verification import MeterVerifier

        verifier = MeterVerifier()
        results = verifier.verify_verse(verse)

        if "verification_details" in results:
            details = results["verification_details"]
            stats = details["pattern_statistics"]

            print("\nResult:")
            print(f"Syllable count: {stats.get('total_syllables', 0)}")
            print(f"Guru count: {stats.get('guru_count', 0)}")
            print(f"Laghu count: {stats.get('laghu_count', 0)}")

            if details.get("is_valid_meter", False):
                print(
                    f"\nValid meter detected: {', '.join(details.get('matched_meters', []))}"
                )
            elif details.get("matched_meters", []):
                print(
                    f"\nPartial match: {', '.join(details.get('matched_meters', []))}"
                )
                print(f"Confidence: {details.get('confidence_score', 0):.2f}%")
            else:
                print("\nNo known meter matched")
        else:
            print("Error in verification")

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    analyze_verse()
