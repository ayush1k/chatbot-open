import re

def extract_workspace_code(messages: list) -> str:
    """
    Extracts all markdown code blocks from the assistant's messages in the history
    and compiles them into a single string separated by newlines and basic markdown dividers.
    """
    extracted_blocks = []
    code_pattern = re.compile(r"```(?:\w+)?\n(.*?)```", re.DOTALL)
    for msg in messages:
        if msg.get("role") == "assistant":
            matches = code_pattern.findall(msg.get("content", ""))
            for match in matches:
                extracted_blocks.append(match.strip())
    if not extracted_blocks:
        return ""
    return "\n\n---\n\n".join(extracted_blocks)
