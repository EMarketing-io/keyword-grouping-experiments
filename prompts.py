def schema_format_instructions():
    return """
Return your output as a valid JSON array.
Each array item must be an object with the following exact fields:

- "Question": string, either "Yes" or "No"
- "Location": string, "Yes" or "No". If "Yes", append a dash and the location name.
- "Type": string, one of "Brand", "Competitor", or "Generic"
- "Product_Service": string, one of "Product", "Service", "Brand", or "Other"
- "Category": string, concise standardized category/niche
- "Properties": array of strings, listing all explicit or implied attributes
- "Intent": string, most accurate search intent
- "Intent_Description": string, short explanation aligned with the chosen intent

Do not include any commentary, text, or fields outside this JSON array.
    """


def get_initial_classification_prompt(keywords: list[str]) -> str:
    return f"""
You are a keyword intent analysis system for digital marketing, capable of working in any industry.

For each keyword, identify and return the required fields described below.
Ensure consistent wording for "Category", "Properties", and "Intent" across similar keywords.

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
- Ensure "Properties" wording is standardized for similar attributes.
- Keep "Intent" consistent for similar keywords.
- Make all outputs concise, standardized, and consistent across the batch.

Here are the current results:
{refined_results}

{schema_format_instructions()}
    """