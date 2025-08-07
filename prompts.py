def schema_format_instructions():
    return """
Return your output as a valid JSON array.
Each array item must be an object with the following exact fields:

- "Question": string, either "Question" or "Not Question"
- "Location": string, either "Location" or "No Location"
- "Type": string, one of "Brand", "Competitor", or "Generic"
- "Product_Service": string, one of "Product", "Service", "Brand", or "Other"
- "Category": string, the main theme of the keyword in proper title case.
- "Properties": string, one key physical, functional, or technical attribute if clearly mentioned or implied. 
                Only include a meaningful product or service feature like "Non-Surgical", "5-Star", "Inverter", etc.
                Leave blank if there is no such attribute.
- "Intent": string, most accurate search intent.
- "Intent_Description": string, short explanation aligned with the chosen intent.

Do not include any commentary, text, or fields outside this JSON array.
    """


def get_initial_classification_prompt(keywords: list[str], brand_name: str) -> str:
    return f"""
You are classifying keywords for marketing intent and structure.

Follow these exact instructions for each keyword:

- "Question": "Question" if the keyword is phrased as a question, otherwise "Not Question".
- "Location": "Location" if any location is mentioned or implied (city, area, near me, etc.); otherwise "No Location".
- "Type": 
    - "Brand" if the keyword contains the brand name "{brand_name}"
    - "Competitor" if it refers to another brand
    - "Generic" if no brand is mentioned
- "Product_Service": Is the keyword referring to a Product, Service, Brand, or Other?
- "Category": Main theme of the keyword. Use proper title case. Keep consistent naming for similar topics.
- "Properties": Only include ONE real, relevant product or service attribute. 
                Must be a concrete characteristic such as technology, rating, feature, or material. 
                Do not include vague or procedural words like: "best", "method", "way", "solution", "how to", "remove", "treatment", "procedure", etc.
                If the keyword contains no such attribute, leave it blank.
- "Intent": User’s likely search intent.
- "Intent_Description": Explain what the user likely wants based on the keyword.

Here are the keywords to classify:
{keywords}

Now classify them and return the result using this JSON structure:
{schema_format_instructions()}
    """


def get_intent_refinement_prompt(initial_results: list[dict]) -> str:
    return f"""
You are refining only the "Intent" and "Intent_Description" fields.

Instructions:
- Review each keyword again.
- Make sure the intent (and its description) clearly match what the user is trying to achieve.
- Keep consistency across similar keyword types.
- Only update "Intent" and "Intent_Description", do not change any other field.

Here is the list:
{initial_results}

Use this structure:
{schema_format_instructions()}
    """


def get_consistency_review_prompt(refined_results: list[dict]) -> str:
    return f"""
You are doing a consistency and final review across all fields.

Instructions:
- Make sure "Question" is either "Question" or "Not Question".
- Make sure "Location" is either "Location" or "No Location".
- Make sure "Category" is consistent for similar keyword themes.
- Ensure "Properties" contains only relevant attributes like features, materials, specifications, or technology.
    - Do NOT use vague words like: best, way, method, fix, how, remove, procedure, multiple.
    - Leave blank if no clear product/service attribute is present.
- Ensure "Intent" and "Intent_Description" are consistent and relevant.

Here is the list:
{refined_results}

Use this format:
{schema_format_instructions()}
    """
