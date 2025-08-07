import pandas as pd
import sys
from keyword_processor import KeywordProcessor

REQUIRED_INPUT_COLS = [
    "Seed Keywords",
    "Keyword",
    "Search Volume",
    "Top of Page Bid (Low Range)",
    "Top of Page Bid (High Range)",
]


def main():
    if len(sys.argv) < 3:
        print("Usage: python main.py <input_file.xlsx> <output_file.xlsx>")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    df = pd.read_excel(input_file)
    missing_cols = [col for col in REQUIRED_INPUT_COLS if col not in df.columns]
    if missing_cols:
        print(f"Error: Missing required columns in input: {missing_cols}")
        sys.exit(1)

    df = df[REQUIRED_INPUT_COLS]
    processor = KeywordProcessor()
    processed_df = processor.process_keywords(df)
    processed_df.to_excel(output_file, index=False)

    print(f"✅ Processing complete. Output saved to {output_file}")


if __name__ == "__main__":
    main()
