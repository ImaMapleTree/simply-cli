_type = type


def __annotated__(decorator):
    def annotated_inner(lazy_def=None, *args, **kwargs):
        if lazy_def:
            return decorator(lazy_def, *args, **kwargs)

        def wrapper(real_def):
            return decorator(real_def, *args, **kwargs)

        return wrapper

    return annotated_inner


def __complex_decorator__(**decorator_flags):
    def inner(outer, *_, **__):
        def real_decorator(cli, *args, **kwargs):
            executed = None
            args = list(args)

            if len(args) != 0:
                executed = args[0]
                args = args[1:]

            args.insert(0, cli)

            def wrapper(f, *_, **__):
                run_args = list(args)

                run_args.insert(1, f)
                if decorator_flags.get("no_wrap") and executed:
                    run_args.insert(2, executed)

                res = outer(*run_args, **kwargs)
                return res

            if executed and decorator_flags.get("no_wrap") is False:
                return wrapper(executed)
            return wrapper

        return real_decorator

    return inner


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

        return command_like

    return description_inner


cmd_description = description
