import pandas as pd
from keyword_processor import KeywordProcessor

REQUIRED_INPUT_COLS = [
    "Seed Keywords",
    "Keyword",
    "Search Volume",
    "Top of Page Bid (Low Range)",
    "Top of Page Bid (High Range)",
]


def main():
    print("🔹 Keyword Intent & Grouping Tool")

    input_file = input("Enter input Excel file name (e.g. input.xlsx): ").strip()
    output_file = input("Enter output Excel file name (e.g. output.xlsx): ").strip()
    brand_name = (
        input("Enter your brand name (used to detect 'Brand' vs 'Competitor'): ")
        .strip()
        .lower()
    )

    try:
        df = pd.read_excel(input_file)
    except Exception as e:
        print(f"❌ Failed to read file: {e}")
        return

    missing_cols = [col for col in REQUIRED_INPUT_COLS if col not in df.columns]
    if missing_cols:
        print(f"❌ Error: Missing required columns in input: {missing_cols}")
        return

    df = df[REQUIRED_INPUT_COLS]

    processor = KeywordProcessor()
    processor.set_brand_name(brand_name)  # 🔥 Pass brand dynamically
    processed_df = processor.process_keywords(df)

    processed_df.to_excel(output_file, index=False)
    print(f"✅ Processing complete. Output saved to: {output_file}")


if __name__ == "__main__":
    main()
