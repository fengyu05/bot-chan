import re


def fstring_format(fstring: str, **kwargs) -> str:
    """
    Formats a string by replacing placeholders with corresponding values from kwargs.

    This function processes placeholders in the form `{key}` where `key` can be
    a nested path like `a.b.c`. It safely handles escaped braces `{{` and `}}`.

    Args:
        fstring (str): The format string containing placeholders.
        **kwargs: Key-value pairs used to replace placeholders in the format string.

    Returns:
        str: The formatted string with placeholders replaced by corresponding values.

    Example:
        >>> fstring_format("{a} {b.c}", a=1, b={"c": "a"})
        '1 a'

        >>> fstring_format("{{ It is }} an example with {a}{b.c}.", a=1, b={"c": "nested"})
        '{ It is } an example with 1nested.'
    """

    def get_nested_value(obj, key):
        keys = key.split(".")
        for k in keys:
            if isinstance(obj, dict):
                if k not in obj:
                    raise KeyError(
                        f"Input invalid: Key '{k}' not found in dictionary when resoloving {key}."
                    )
                obj = obj[k]
            else:
                if not hasattr(obj, k):
                    raise KeyError(
                        f"Input invalid: Attribute '{k}' not found in object when resoloving {key}."
                    )
                obj = getattr(obj, k)
        return obj

    # Escape "{{" and "}}" to gracefully handle them as "{" and "}" respectively
    fstring = fstring.replace("{{", "\u007b").replace("}}", "\u007d")

    # Regular expression to match valid placeholder patterns
    pattern = re.compile(r"\{([a-zA-Z_][a-zA-Z0-9_]*(\.[a-zA-Z0-9_]+)*)\}")

    placeholders = pattern.findall(fstring)

    for match in placeholders:
        placeholder = match[0]
        value = get_nested_value(kwargs, placeholder)
        fstring = fstring.replace(f"{{{placeholder}}}", str(value))

    # Replace temporary markers with actual braces
    fstring = fstring.replace("\u007b", "{").replace("\u007d", "}")

    return fstring
