import abc

import simplycli
from simplycli.decorators import __annotated__
from simplycli.meta import CommandLike, AbstractFunctionCommandWrapper, forward_meta


class __BundleCommand__(AbstractFunctionCommandWrapper):
    def __init__(self, command_like: CommandLike, properties):
        self.command_like = command_like

        self.__bundle_properties__ = properties
        self.__bundle__ = None

        forward_meta(self.command_like, self)

    def signature(self) -> CommandLike:
        return self.command_like

    def invoke(self, *args, **kwargs):
        args = list(args)
        args.insert(0, self.__bundle__)
        return self.command_like(*args, **kwargs)


class Bundle(abc.ABC):
    """
    This class serves as a simple interface to dynamically add and remove batches of commands. To create a "bundle"
    of commands, you should create a subclass of this and annotate all desired commands with `@Bundle.command`.

    The commands in the bundle can then be added/removed by method available in `CLI.bundles`
    """

    @staticmethod
    @__annotated__
    def command(command_like: CommandLike, **kwargs):
        """
        Registers a method as a command, this annotation is identical to :meth:`CLI.command` except it requires the method
        to be present in a subclass of :class:`Bundle`.
        :param command_like: the method to register
        :param kwargs: the kwargs to register the command with
        """
        return __BundleCommand__(command_like, kwargs)

    def __commands__(self) -> list[__BundleCommand__]:
        cmds = []
        for attr in dir(self):
            val = getattr(self, attr)
            if getattr(val, "__bundle_properties__", None) is not None:
                val.__bundle__ = self
                cmds.append(val)
        return cmds


class BundleManager:
    def __init__(self, cli: "simplycli.CLI"):
        self._bundle_map: dict[Bundle, list[__BundleCommand__]] = {}

        self.cli = cli

    def active(self) -> set[Bundle]:
        return self._bundle_map.keys()

    def apply(self, bundle: Bundle):
        if bundle in self._bundle_map:
            cmds = self._bundle_map[bundle]
            new_cmds = [c for c in bundle.__commands__() if c not in cmds]
            for cmd in new_cmds:
                self.cli.command(cmd, **cmd.__bundle_properties__)
                cmds.append(cmd)
            return

        cmds = bundle.__commands__()
        self._bundle_map[bundle] = cmds
        for command in cmds:
            self.cli.command(command, **command.__bundle_properties__)

    def remove(self, bundle: Bundle):
        if bundle in self._bundle_map:
            cmds = self._bundle_map.pop(bundle)
            for command in cmds:
                self.cli.unregister(command)
