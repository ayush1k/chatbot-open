def format_project_context(readme_context: str) -> str:
    """
    Formats the raw text project context by adding structured instructions
    explaining multi-file tag delimiters.
    """
    if not readme_context:
        return ""
    return (
        "The provided context may contain multiple files. "
        "Files will be denoted by the syntax '--- START FILE: filename ---' and '--- END FILE ---'. "
        "Treat these as distinct files in the project structure.\n\n"
        f"Project context:\n{readme_context}"
    )
