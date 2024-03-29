def hello_world(name: str = "You") -> str:
    """Returns a greeting string for a given name.

    Args:
        name (str, optional): The name of the person to greet. Defaults to
        "You".

    Returns:
        str: A greeting string.
    """
    capitalized_name = name.capitalize()
    return f"Hello, {capitalized_name}!"
