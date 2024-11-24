import re

def get_leading_emoji(text: str) -> str:
    pattern = r'^:(\w+):'
    match = re.match(pattern, text)
    if match:
        return match.group(1)
    else:
        return ""
    
def strip_leading_emoji(text: str) -> str:
    pattern = r'^:(\w+):'
    match = re.match(pattern, text)
    if match:
        # Remove the leading emoji pattern from the text
        return re.sub(pattern, '', text, 1)
    else:
        return text