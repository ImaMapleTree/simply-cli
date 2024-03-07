import unittest
from simplycli.arg import *


class ArgTests(unittest.TestCase):
    def test_basic_arg_parsing(self):
        arg = Arg(0)

        self.assertEqual(3, arg.parse("3", int))
        self.assertEqual("hello", arg.parse("hello", str))
        self.assertEqual(True, arg.parse("true", bool))

    def test_positional_arg_parsing(self):
        arg = Arg(2)

        self.assertEqual(2, arg.parse("0 1 2", int))

        arg = Arg(2, required=True)

        self.assertRaises(ArgumentError, arg.parse, "01234", int)

        arg = Arg(2, default=100)

        self.assertEqual(100, arg.parse("01234", int))

        arg = Arg(3)

        self.assertEqual("two words", arg.parse('one two one-word "two words"', str))

    def test_named_arg_parsing(self):
        arg = Arg("--value")

        self.assertEqual("red", arg.parse("--value red", str))
        self.assertEqual("pencil or paper", arg.parse('junk --value "pencil or paper" more junk', str))

        arg = Arg("--value", required=True)

        self.assertRaises(ArgumentError, arg.parse, "nothing but junk here", str)

        arg = Arg("--value", default="defaulted")

        self.assertEqual("defaulted", arg.parse("this should default", str))

    def test_arg_aliases(self):
        arg = Arg("-s", aliases=["--short"])

        self.assertEqual(56, arg.parse("--short 56", int))
        self.assertEqual(123, arg.parse("-s 123", int))


if __name__ == '__main__':
    unittest.main()
