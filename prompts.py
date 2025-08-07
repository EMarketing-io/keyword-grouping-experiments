def schema_format_instructions():
    return """
Return your output as a valid JSON array.
Each array item must be an object with the following exact fields:

- "Question": string, either "Question" or "Not Question"
- "Location": string, either "Location" or "No Location"
- "Type": string, one of "Brand", "Competitor", or "Generic"
- "Product_Service": string, one of "Product", "Service", "Brand", or "Other"
- "Category": string, the main theme of the keyword in proper title case.
- "Properties": string, the single most important distinguishing attribute of the keyword based on its meaning and intent. 
                 Do not just copy words; analyze and infer the attribute. 
                 Example: If the keyword says "without surgery", the property is "Non-Surgical".
                 If no clear property is implied, leave blank.
- "Intent": string, most accurate search intent
- "Intent_Description": string, short explanation aligned with the chosen intent

Do not include any commentary, text, or fields outside this JSON array.
    """


def get_initial_classification_prompt(keywords: list[str]) -> str:
    return f"""
Classify each keyword accurately according to the following rules:

- "Question": "Question" if in question form, else "Not Question".
- "Location": "Location" if a location is mentioned or implied, else "No Location".
- "Category": Main theme in proper title case.
- "Properties": One most important attribute inferred from the keyword's meaning. 
                 This may be a feature, technology, specification, or style. 
                 Do not copy exact words; interpret the intent. 
                 Leave blank if no property exists.
- "Type": Brand, Competitor, or Generic.
- "Product_Service": Product, Service, Brand, or Other.
- "Intent": Most accurate search intent.
- "Intent_Description": Short explanation of the user's likely goal.

Keywords:
{keywords}

{schema_format_instructions()}
    """


def get_intent_refinement_prompt(initial_results: list[dict]) -> str:
    return f"""
Refine only the "Intent" and "Intent_Description" fields.

- Ensure intent reflects the user's likely goal.
- Keep consistency for similar keywords.
- Descriptions must match the refined intent exactly.

Initial results:
{initial_results}

{schema_format_instructions()}
    """


def get_consistency_review_prompt(refined_results: list[dict]) -> str:
    return f"""
Review and finalize all fields for consistency.

- "Question" must be either "Question" or "Not Question".
- "Location" must be either "Location" or "No Location".
- "Category" must be consistent for similar themes.
- "Properties" must be the single most important distinguishing attribute inferred from the keyword. 
                 Do not just copy words; analyze the meaning.
- Leave "Properties" blank if no property exists.
- "Intent" must be consistent for similar keywords.

Here are the current results:
{refined_results}

{schema_format_instructions()}
    """
