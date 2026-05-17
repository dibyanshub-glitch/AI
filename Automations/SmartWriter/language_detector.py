def detect_language(prompt):

    prompt = prompt.lower()

    if "python" in prompt:
        return "python", ".py"

    if "html" in prompt or "website" in prompt:
        return "html", ".html"

    if "javascript" in prompt or "js" in prompt:
        return "javascript", ".js"

    if "react" in prompt:
        return "react", ".jsx"

    return "text", ".txt"
