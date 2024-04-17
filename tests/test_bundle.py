import unittest
from simplycli import CLI, Arg
from simplycli.bundle import Bundle


class TestBundle(Bundle):
    @Bundle.command
    def one(self):
        return 1

    @Bundle.command
    def add(self, n1: int = Arg(0), n2: int = Arg(1)):
        return n1 + n2

    @Bundle.command(aliases=["subtract"], args=[Arg(0), Arg(1)])
    def sub(self, n1: int, n2: int):
        return n1 - n2


class MyTestCase(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cli = CLI()

    def test_register_and_unregister_bundle(self):
        result = self.cli.process_input("one")
        self.assertIsNone(result)

        bundle = TestBundle()
        self.cli.bundles.apply(bundle)

        result = self.cli.process_input("one")
        self.assertEqual(1, result)


if __name__ == '__main__':
    unittest.main()
