import abc
from typing import Callable, TypeAlias, Union

CommandLike: TypeAlias = Union[Callable, "AbstractCommandClass"]

META_PROPERTIES = [
    "__description__",
    "__boundcommand__"
    "__bundle_properties__",
    "__bundle__"
]


def forward_meta(source, target):
    for prop in META_PROPERTIES:
        value = getattr(source, prop, None)
        if value is not None:
            setattr(target, prop, value)


class AbstractFunctionCommandWrapper(abc.ABC):
    """
    A niche class that must be used on function wrapper classes, or more specifically, classes that can be invoked
    via teh __call__ method.
    """

    @abc.abstractmethod
    def signature(self) -> CommandLike:
        """
        Returns the base callable associated with this class.
        :return: The base callable
        """
        raise NotImplementedError

    @abc.abstractmethod
    def invoke(self, *args, **kwargs):
        """
        Invokes this wrapper with the given arguments.
        :param args: Invocation arguments.
        :param kwargs: Invocation keyword arguments.
        :return: The result of the function invocation.
        """
        raise NotImplementedError

    def __getattribute__(self, item):
        if item == "__name__":
            return self.signature().__name__
        return super().__getattribute__(item)

    def __call__(self, *args, **kwargs):
        return self.invoke(*args, **kwargs)


class AbstractCommandClass(abc.ABC):
    """
    Provides a template class for use with :func:`@CLI.command <CLI.command>`, however, classes do not need to inherit
    this class to be an eligible command-class. They simply just need to implement the __execute__ method.
    """

    __description__ = None
    """
    An optional description for the command. You can change this description by modifying the value of this variable.
    """

    @staticmethod
    @abc.abstractmethod
    def __execute__():
        """
        This method is called whenever `this` command is successfully matched. Implementations of this method can
        choose any function signature.
        """
        raise NotImplementedError