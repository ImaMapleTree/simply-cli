from functools import wraps

_type = type


def description(content: str):
    """
    A decorator for giving a command-like object a description
    :param content: The description of the command
    """
    if not isinstance(content, str):
        raise ValueError(f"description content must be type string, instead got {type(content)}")

    def description_inner(command_like):
        command_like.__description__ = content
        if getattr(command_like, "__boundcommand__", None):
            command_like.__boundcommand__.description = content

        @wraps(command_like)
        def wrapper(*args, **kwargs):
            return command_like(*args, **kwargs)

        return wrapper

    return description_inner


cmd_description = description
