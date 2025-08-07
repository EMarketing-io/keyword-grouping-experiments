import pandas as pd
import time
import json
from typing import List
from pydantic import BaseModel, RootModel
from langchain.schema import HumanMessage
from langchain.output_parsers import PydanticOutputParser
from langchain_openai import ChatOpenAI
from prompts import (
    get_initial_classification_prompt,
    get_intent_refinement_prompt,
    get_consistency_review_prompt,
)
from config import OPENAI_MODEL, BATCH_SIZE, TEMPERATURE, MAX_RETRIES, OPENAI_API_KEY


class KeywordClassification(BaseModel):
    Question: str
    Location: str
    Type: str
    Product_Service: str
    Category: str
    Properties: str
    Intent: str
    Intent_Description: str


class KeywordBatch(RootModel[List[KeywordClassification]]):
    pass


class KeywordProcessor:
    def __init__(self):
        self.brand_name = None
        self.client = ChatOpenAI(
            model=OPENAI_MODEL, temperature=TEMPERATURE, api_key=OPENAI_API_KEY
        )
        self.parser = PydanticOutputParser(pydantic_object=KeywordBatch)

    def set_brand_name(self, brand_name: str):
        self.brand_name = brand_name.strip().lower()

    def call_llm(self, prompt: str) -> List[dict]:
        retries = 0
        while retries < MAX_RETRIES:
            try:
                format_instructions = self.parser.get_format_instructions()
                full_prompt = f"{prompt}\n\nFollow this format:\n{format_instructions}"
                response = self.client.invoke([HumanMessage(content=full_prompt)])
                parsed = self.parser.parse(response.content)
                return [item.dict() for item in parsed.root]
            except Exception as e:
                retries += 1
                print(f"⚠️ Retry {retries}/{MAX_RETRIES} due to error: {e}")
                time.sleep(2**retries)
        return []

    def process_batch(self, batch_keywords: List[str]) -> List[dict]:
        prompt = get_initial_classification_prompt(batch_keywords, self.brand_name)
        initial_results = self.call_llm(prompt)
        if not initial_results:
            return []

        refined_intents = (
            self.call_llm(get_intent_refinement_prompt(initial_results))
            or initial_results
        )
        final_results = (
            self.call_llm(get_consistency_review_prompt(refined_intents))
            or refined_intents
        )

        for entry in final_results:
            if entry["Question"] not in ["Question", "Not Question"]:
                entry["Question"] = "Not Question"
            if entry["Location"] not in ["Location", "No Location"]:
                entry["Location"] = "No Location"
            if not entry.get("Properties") or len(entry["Properties"].strip()) == 0:
                entry["Properties"] = ""

        return final_results

    def normalize_categories_with_llm(self, df: pd.DataFrame) -> pd.DataFrame:
        unique_categories = sorted(df["Category"].dropna().unique().tolist())
        if not unique_categories:
            return df 

        prompt = f"""
You are helping standardize keyword categories for ad grouping.

Here is a list of raw category labels:
{unique_categories}

Please group similar ones together and assign a single clean, consistent name to each group.

Return output as a strict JSON object like this:
{{"Old Category A": "Standard Group 1", "Old Category B": "Standard Group 1", "Old Category C": "Standard Group 2"}}

⚠️ Rules:
- Use proper JSON syntax — keys and values must be in double quotes.
- Return only the JSON object, with no extra commentary or explanation.
- Be concise and consistent.
- Do not create new category names — just standardize the ones provided.
"""

        try:
            response = self.client.invoke([HumanMessage(content=prompt)])
            raw_json = response.content.strip()

            mapping = json.loads(raw_json)
            df["Category"] = df["Category"].map(mapping).fillna(df["Category"])
            return df

        except Exception as e:
            print("⚠️ Failed to normalize categories:", e)
            return df

    def process_keywords(self, df: pd.DataFrame) -> pd.DataFrame:
        keywords = df["Keyword"].dropna().tolist()
        all_results = []
        total_batches = (len(keywords) - 1) // BATCH_SIZE + 1

        for i in range(0, len(keywords), BATCH_SIZE):
            batch = keywords[i : i + BATCH_SIZE]
            print(
                f"Processing batch {i // BATCH_SIZE + 1} of {total_batches} ({len(batch)} keywords)..."
            )
            results = self.process_batch(batch)
            all_results.extend(results)

        results_df = pd.DataFrame(all_results)

        # Normalize categories dynamically using LLM (safe with json)
        results_df = self.normalize_categories_with_llm(results_df)

        merged_df = pd.concat(
            [df.reset_index(drop=True), results_df.reset_index(drop=True)], axis=1
        )

        final_columns = [
            "Seed Keywords",
            "Keyword",
            "Search Volume",
            "Top of Page Bid (Low Range)",
            "Top of Page Bid (High Range)",
            "Question",
            "Location",
            "Type",
            "Product_Service",
            "Category",
            "Properties",
            "Intent",
            "Intent_Description",
        ]
        final_columns = [col for col in final_columns if col in merged_df.columns]
        return merged_df[final_columns]
