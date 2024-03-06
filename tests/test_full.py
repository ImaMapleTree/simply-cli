import unittest

from simplycli import CLI, Arg, ArgumentError, AbstractCommandClass
from simplycli.decorators import description


def create_commands(cli: CLI):
    @cli.command
    def one():
        return 1

    @cli.command(aliases=["_two_"])
    def two():
        return 2

    @cli.command(args=[Arg(0), Arg(1)])
    def add(o1: int, o2: int):
        return o1 + o2

    @cli.command
    def sub(o1: int = Arg(0), o2: int = Arg(1)):
        return o1 - o2

    @cli.command
    def mul(o1: int = Arg(0, required=True), o2: int = Arg(1, default=2)):
        return o1 * o2

    @cli.command
    @description("Divides two numbers v1")
    def div(o1: int = Arg("--numerator"), o2: int = Arg("--denominator"), remainder: bool = Arg("--remainder")):
        if remainder:
            return o1 % o2
        return o1 / o2

    @description("Divides two numbers v2")
    @cli.command(args=[
        Arg("--numerator", type=int),
        Arg("--denominator", type=int),
        Arg("--remainder", type=bool)
    ])
    def div2(o1, o2, remainder):
        return div(o1, o2, remainder)


    @cli.command
    class Basic:
        def __execute__(self):
            return 30

    @cli.command
    class Basic2(AbstractCommandClass):
        __description__ = "Returns the provided message"

        @staticmethod
        def __execute__(message: str = Arg(0)):
            return message


class CommandTestCase(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cli = CLI()
        create_commands(self.cli)

    def test_commands(self):
        self.assertEqual(1, self.cli.process_input("one"))
        self.assertEqual(2, self.cli.process_input("_two_"))

        self.assertEqual(14, self.cli.process_input("add 5 9"))
        self.assertEqual(6, self.cli.process_input("sub 10 4"))

        self.assertEqual(4, self.cli.process_input("mul 2"))
        self.assertEqual(12, self.cli.process_input("mul 2 6"))
        self.assertRaises(ArgumentError, self.cli.process_input, "mul")

        self.assertEqual(3, self.cli.process_input("div --numerator 6 --denominator 2"))
        self.assertEqual(0, self.cli.process_input("div --numerator 6 --denominator 2 --remainder"))
        self.assertEqual("Divides two numbers v1", self.cli.find_command("div").description)

        self.assertEqual(3, self.cli.process_input("div2 --numerator 6 --denominator 2"))
        self.assertEqual(0, self.cli.process_input("div2 --numerator 6 --denominator 2 --remainder"))
        self.assertEqual("Divides two numbers v2", self.cli.find_command("div2").description)

        self.assertEqual(30, self.cli.process_input("basic"))
        self.assertEqual("message", self.cli.process_input("basic2 message"))
        self.assertEqual("Returns the provided message", self.cli.find_command("basic2").description)




if __name__ == '__main__':
    unittest.main()
