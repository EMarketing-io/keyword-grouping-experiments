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


def create_keyword_grouping(df: pd.DataFrame, writer):
    all_blocks = []

    for seed in df["Seed Keywords"].unique():
        seed_keywords = df[df["Seed Keywords"] == seed]["Keyword"].dropna().tolist()
        groups = [seed_keywords[i : i + 20] for i in range(0, len(seed_keywords), 20)]
        max_len = max(len(g) for g in groups) if groups else 0
        header_row = [f"Seed Keyword: {seed}"] + [f"Group {i+1}" for i in range(len(groups))]
        header_df = pd.DataFrame([header_row])
        data_rows = []
        
        for row_idx in range(max_len):
            row = [""]
            for g in groups:
                row.append(g[row_idx] if row_idx < len(g) else "")
            data_rows.append(row)

        data_df = pd.DataFrame(data_rows, columns=header_df.columns)
        block_df = pd.concat([header_df, data_df], ignore_index=True)
        empty_df = pd.DataFrame([[""] * len(header_df.columns)], columns=header_df.columns)
        all_blocks.append(block_df)
        all_blocks.append(empty_df)

    final_df = pd.concat(all_blocks, ignore_index=True)
    final_df.to_excel(writer, sheet_name="Keywords Grouping", index=False)


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

    with pd.ExcelWriter(output_file, engine="openpyxl") as writer:
        processed_df.to_excel(writer, sheet_name="Processed Keywords", index=False)
        create_keyword_grouping(processed_df, writer)

    print(f"✅ Processing complete. Output saved to {output_file} with 'Processed Keywords' and 'Keywords Grouping' sheets.")


if __name__ == "__main__":
    main()