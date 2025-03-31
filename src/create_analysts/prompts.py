analyst_instructions = """
You are tasked with creating a set of analyst personas. Follow these instructions carefully:
1. First review the research topic:
{topic}
2. Estimate any editorial feedback that been optionally provided to guide creation of the analysts:
{human_analyst_feedback}
3. Determine the most interesting themes based upon documents and/or feedback above
4. Pick the top {max_analysts} themes.
5. Assign one analyst to each theme
"""