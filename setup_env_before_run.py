#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Setup environment before running Sanskrit meter tools

This script must be imported before running any of the Sanskrit meter tools.
"""

import os
import sys
import json
import codecs
import warnings

# Suppress warnings
warnings.filterwarnings("ignore", message="A module that was compiled using NumPy 1.x")
warnings.filterwarnings("ignore", message="numpy.core._multiarray_umath")
warnings.filterwarnings("ignore", category=RuntimeWarning)
warnings.filterwarnings("ignore", category=ImportWarning)

# Add chandas to sys.path
chandas_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "chandas")
if chandas_path not in sys.path:
    sys.path.insert(0, chandas_path)

# Patch json.load for UTF-8 support
original_json_load = json.load

def utf8_json_load(file_obj, *args, **kwargs):
    if isinstance(file_obj, codecs.StreamReader):
        return original_json_load(file_obj, *args, **kwargs)
    
    try:
        # Get file path
        file_path = file_obj.name
        # Close the original file
        file_obj.close()
        # Reopen with UTF-8
        with codecs.open(file_path, "r", encoding="utf-8") as f:
            return original_json_load(f, *args, **kwargs)
    except Exception as e:
        # Fallback
        return original_json_load(file_obj, *args, **kwargs)

json.load = utf8_json_load
