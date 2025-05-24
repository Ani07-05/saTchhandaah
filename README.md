# Sanskrit Meter Verification System

This tool helps you analyze Sanskrit verses and identify their metrical patterns.

## Features

- Identify meters in Sanskrit verses
- Analyze syllable patterns (guru/laghu)
- Calculate metrical statistics
- Beautiful, colorful CLI interface

## Installation

1. Make sure you have Python 3.6+ installed
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

### Quick Analysis

For the most user-friendly experience, run:

```
python analyze.py
```

This will start the interactive verse analyzer with a beautiful interface. 
Enter your verse and press Enter on a blank line to analyze it.

### Alternative Methods

1. **Command Line Interface:**
   ```
   python sanskrit_verse_analyzer.py -v "वागर्थाविव संपृक्तौ वागर्थप्रतिपत्तये।"
   ```

2. **Analyze from File:**
   ```
   python sanskrit_verse_analyzer.py -f verse.txt
   ```

3. **Simple Interface:**
   ```
   python analyze_custom_verse.py
   ```

## Examples

### Example 1 - Anuṣṭup (Śloka)

```
वागर्थाविव संपृक्तौ वागर्थप्रतिपत्तये।
जगतः पितरौ वन्दे पार्वतीपरमेश्वरौ॥
```

### Example 2 - Vasantatilakā

```
आयाति कुङ्कुमरसैः पुलकाङ्कितेव 
याति प्रियानुगमने विवशा नितान्तम्।
प्रातः प्रदोषसमये च विवर्णभावं 
संध्या प्रियप्रियसखी न मृषा कवीनाम्॥
```

## Troubleshooting

If you encounter issues:

1. Try running the fix_all.py script:
   ```
   python fix_all.py
   ```

2. Make sure you have the correct version of NumPy:
   ```
   pip install numpy==1.24.3 --force-reinstall
   ```

3. Set up the environment before running:
   ```
   import setup_env_before_run
   ```

## License

This project uses the chandas library for Sanskrit meter identification.

## Credits

- Sanskrit NLP tools by Sanskrit Programmer
- Chandas library for meter identification