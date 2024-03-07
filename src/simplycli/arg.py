import inspect
import re
from typing import Union, Any, Callable
from simplycli import cli


class ArgumentError(Exception):
    """
    Exception raised when an argument is not properly provided.
    """

    def __init__(self, message=None):
        """
        Initialize the ArgumentError.

        :param message: A message describing the error (optional).
        """
        super().__init__(message)


class CommandSignatureError(Exception):
    """
    Exception raised when a command has an invalid or incompatible signature.
    """

    def __init__(self, message=None):
        """
        Initialize the ArgumentError.

        :param message: A message describing the error (optional).
        """
        super().__init__(message)

class SegmentString:
    def __init__(self, raw_input: str):
        self.segments = SegmentString._parse_segments(raw_input)
        self.matched: set[str] = set()
        self.raw = raw_input


    @staticmethod
    def _parse_segments(raw_input: str):
        segments = []
        delimiters = []
        segment = ""
        # split raw string into space separated terms
        for character in raw_input:
            if len(delimiters) == 0 and character.isspace():
                segments.append(segment)
                segment = ""
            elif character == "'" or character == '"':
                if character in delimiters:
                    delimiters.pop()
                else:
                    if len(delimiters) == 0:
                        delimiters.append(character)
                    else:
                        segment += character
            else:
                segment += character

        if segment != "":
            segments.append(segment)

        return segments

    def match(self, details: "ArgParser") -> int:
        if details.aliases:
            aliases = list(details.aliases)
        else:
            aliases = []
        aliases.append(details.name)

        for alias in aliases:
            try:
                index = self.segments.index(alias)
                self.matched.add(self.segments[index])
                return index
            except ValueError:
                pass
        return None

    def unmatched(self):
        return [segment for segment in self.segments if segment not in self.matched]

    def __contains__(self, item: "ArgParser"):
        return item in self.matched

    def __len__(self):
        return len(self.segments)

    def __getitem__(self, item):
        return self.segments[item]

class ArgParser:
    """
    A class used by :class:`Arg` for parsing a raw string into a value
    """

    def __init__(self, name: Union[str, int], aliases: list[str], position: int, required: bool, default: Any, expected_type: type):
        self.name = name
        self.aliases = aliases
        self.position = position
        self.required = required
        self.default = default
        self.expected_type = expected_type

    def parse(self, segments: SegmentString, expected_type: type) -> Any:
        """
        Parses a `full` input string, extracting and returning the value of `this` argument in relation to the input.

        :param segments: The :class:`SegmentString` to parse
        :param expected_type: The expected type of the return value, which **must contain a `from-string constructor`**
            **OR** a function that takes the extracted string value as an input and returns a value output.
        :return: The parsed value of this argument.
        """
        return __ARG_PARSING_IMPLEMENTATION__(self, segments, expected_type)

    @staticmethod
    def default_parse(details: "ArgParser", segments: SegmentString, expected_type: Union[type, Callable[[str], Any]]) -> Any:
        named_segment_index = segments.match(details)

        # if argument is positional
        if details.position is not None:
            if details.position >= len(segments):
                if details.required and not details.name:
                    raise ArgumentError(f"expected positional argument at {details.position}")
            else:
                # return segment at position
                value_segment = segments[details.position]
                segments.matched.add(value_segment)
                return expected_type(value_segment)

        if details.name:
            # found segment that matches details.name
            if named_segment_index is not None:
                if len(segments) > named_segment_index + 1:
                    value_segment = segments[named_segment_index + 1]
                    segments.matched.add(value_segment)
                    return expected_type(value_segment)
                elif expected_type is bool:  # if the expected type is a boolean then the presence alone should ret true
                    return True
                else:
                    raise ArgumentError(f"no value provided for argument \"{details.name}\"")
            # no such segment
            if details.required:
                raise ArgumentError(f"expected named argument \"{details.name}\"")

        return details.default


__ARG_PARSING_IMPLEMENTATION__ = ArgParser.default_parse
"""
The parsing method used by :func:`ArgParser.parse`. This defaults to :func:`ArgParser.default_parse`
"""


class ArgMatcher:
    _empty_type_ = inspect._empty

    def __init__(self, command: "cli.Command") -> list[Any]:
        self.func: Callable = None

        if command.is_class:
            self.func = command.command_like.__execute__
        elif command.__wrapped_command__:
            self.func = command.command_like.signature()
        else:
            self.func = command.command_like

        self.parameters = list(inspect.signature(self.func).parameters.values())
        self.command = command

        self.__vargs__ = False
        self.__validate_arguments__()

    def match_arguments(self, raw_input: str) -> list[Any]:
        """
        Parses an input string into a list of values by matching the string to respective arguments.

        :param raw_input: The input string to parse.
        :return: A list of parsed values.
        """

        segments = SegmentString(raw_input)

        ignore = 0
        arguments = []
        for i in range(len(self.parameters)):
            parameter = self.parameters[i]
            default = parameter.default

            if self.command.args is not None and i - ignore < len(self.command.args):
                default = self.command.args[i - ignore]

            expected_type = parameter.annotation
            if expected_type is ArgMatcher._empty_type_:
                expected_type = str

            # handle case where `Arg` class is used instead of `Arg` instance
            if default is Arg:
                default = Arg.dynamic()

            if parameter.name == "self":
                ignore += 1
                if self.command.is_class:
                    arguments.append(self.command.get_instance())
            elif expected_type is cli.Command:
                ignore += 1
                arguments.append(self.command)
            elif isinstance(default, Arg):  # special syntax where default value is Arg() class used as an 'annotation'
                default.__fill_info__(parameter.name)

                if default.expected_type:   # transform the input value into the arg's expected type
                    value = default.parse(segments, default.expected_type)
                else:                       # otherwise transform it into the parameter's annotated type
                    value = default.parse(segments, expected_type)

                arguments.append(value)
            elif default is not ArgMatcher._empty_type_:
                arguments.append(default)

        if self.__vargs__:
            arguments.extend(segments.unmatched())

        return arguments

    def __validate_arguments__(self):
        for i in range(len(self.parameters)):
            parameter = self.parameters[i]

            if parameter.name == "self" and (not self.command.is_class and not self.command.__wrapped_command__):
                raise CommandSignatureError(f"command function cannot contain argument named \"self\" unless part of a class (function={self.command.name})")
            if str(parameter).startswith("**"):
                raise CommandSignatureError(f"kwargs not supported in command function signature")
            elif str(parameter).startswith("*"):
                if i + 1 < len(self.parameters):
                    raise CommandSignatureError(f"function requires vargs as last parameter in function signature")
                self.__vargs__ = True

class Arg:
    """
    Represents an argument in a function signature, which can be identified by either its name or position.
    """

    def __init__(self, name_or_position: Union[str, list[str], int],
                 /, name: str = None, position: int = None, aliases: list[str] = None, required: bool = False,
                 default: Any = None, type: "type" = None):
        """
        Represents an argument in a function signature, which can be identified by either its name or position.

        :param name_or_position: Either the name (str) or position (int) of the argument.
        :param name: The name of the argument (optional).
        :param position: The position of the argument (optional).
        :param aliases: Additional aliases for the argument (optional).
        :param required: Whether the argument is required (default is False).
        :param default: Default value for the argument (default is None).
        :param type: The expected type of the argument (if None uses the parameter's annotated type, or str if not present).
        """

        self.name = None
        self.aliases = aliases
        self.position = None

        if isinstance(name_or_position, str):
            self.name = name_or_position
        elif isinstance(name_or_position, int):
            self.position = name_or_position
        else:
            raise ValueError(
                f"name_or_position argument must be either str, int, or list[str], instead got {type(name_or_position)}")

        # if name and/or position have been declared via kwargs, override the above declarations
        if name:
            self.name = name
        if position is not None:
            if position < 0:
                raise ValueError(f"position cannot be less than 0 ({position} < 0)")
            self.position = position

        self.required = required
        self.default = default
        self.expected_type = type

        # initialize arg parser
        self._parser = ArgParser(self.name, self.aliases, self.position, self.required, self.default, self.expected_type)
        self.__prefix__ = None
        self.__dynamic__ = False

    @staticmethod
    def named(name: str, required: bool = False, default: Any = None):
        """
        Creates an instance of `Arg` representing an argument identified by name.

        :param name: The name of the argument.
        :param required: Whether the argument is required (default is False).
        :param default: Default value for the argument (default is None).
        :return: An instance of `Arg`.
        """
        return Arg(name, required=required, default=default)

    @staticmethod
    def position(position: int, required: bool = False, default: Any = None):
        """
        Creates an instance of :class:`Arg` representing an argument identified by position.

        :param position: The position of the argument.
        :param required: Whether the argument is required (default is False).
        :param default: Default value for the argument (default is None).
        :return: An instance of :class:`Arg`.
        """
        return Arg(position, required=required, default=default)

    @staticmethod
    def dynamic(prefix="--"):
        """
        Creates an argument that automatically sets its name to prefix + the name of the parameters it's annotated on.
        :return: An instance of :class:`Arg`.
        """
        arg = Arg("__DYNAMIC__")
        arg.name = None  # reset name back to None so that argument will dynamically acquire name
        arg.__prefix__ = prefix
        return arg

    def parse(self, segments: SegmentString, expected_type: Union[type, Callable[[str], Any]]) -> Any:
        """
        Parses a `full` input string, extracting and returning the value of `this` argument in relation to the input.

        :param segments: The :class:`SegmentString` to parse.
        :param expected_type: The expected type of the return value, which **must contain a `from-string constructor`**
            **OR** a function that takes the extracted string value as an input and returns a value output.
        :return: The parsed value of this argument.
        """
        return self._parser.parse(segments, expected_type)

    def __fill_info__(self, parameter: inspect.Parameter):
        if self.name is None and self.position is None:
            prefix = "" if self.__prefix__ is None else self.__prefix__
            self.name = prefix + parameter
