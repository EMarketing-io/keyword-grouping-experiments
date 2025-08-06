def schema_format_instructions():
    """
    Schema description for LLM output (matches Pydantic model in keyword_processor.py).
    """
    return """
Return your output as a valid JSON array.
Each array item must be an object with the following exact fields:

- "Question": string, either "Yes" or "No"
- "Location": string, "Yes" or "No". If "Yes", append a dash and the location name.
- "Type": string, one of "Brand", "Competitor", or "Generic"
- "Product_Service": string, one of "Product", "Service", "Brand", or "Other"
- "Category": string, a concise, properly formatted name for the main theme of the keyword.
               Write it in proper title case and ensure consistency across similar keywords.
               Example: "Non-Surgical Double Chin Reduction", "Laser Hair Removal"
- "Properties": string, the single most relevant modifier or characteristic from the keyword.
                This should capture the most important detail that distinguishes the keyword.
                Examples: "non-surgical", "cost", "near me", "best", "price"
- "Intent": string, most accurate search intent
- "Intent_Description": string, short explanation aligned with the chosen intent

Do not include any commentary, text, or fields outside this JSON array.
    """


def get_initial_classification_prompt(keywords: list[str]) -> str:
    return f"""
You are a keyword intent analysis system for digital marketing, capable of working in any industry.

For each keyword, identify and return the required fields described below.

Rules for Category:
- Derive from the main theme of the keyword.
- Write in proper title case (capitalize main words).
- Keep it consistent across similar keywords.
- Avoid redundant descriptors that are already in properties.

Rules for Properties:
- Only output ONE best property (single string).
- Choose the most relevant modifier from the keyword (location, feature, benefit, material, style, treatment type, etc.).
- If multiple modifiers exist, choose the one most critical to the searcher's decision.

Keywords:
{keywords}

{schema_format_instructions()}
    """


def get_intent_refinement_prompt(initial_results: list[dict]) -> str:
    return f"""
You have classified keywords. Now focus only on refining the "Intent" and "Intent_Description" fields.

For each keyword:
- Reconsider the intent based on the actual user goal.
- Distinguish between research, comparison, and action-oriented searches.
- Keep the intent description aligned with the new intent.
- Maintain consistency across similar keywords.

Initial results:
{initial_results}

{schema_format_instructions()}
    """


def get_consistency_review_prompt(refined_results: list[dict]) -> str:
    return f"""
You have classified keywords with refined intents. Now:
- Ensure "Category" wording is identical for similar concepts.
- Ensure "Properties" are consistent across similar keywords.
- Keep "Intent" consistent for similar keywords.
- Make all outputs concise, standardized, and consistent across the batch.

Here are the current results:
{refined_results}

{schema_format_instructions()}
    """
