import unittest

from simplycli import CLI


class CLITestCase(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cli = None

    def setUp(self):
        self.cli = CLI()

    def test_command_creation(self):
        @self.cli.command
        def ping():
            return "pong"

        self.assertEqual("pong", self.cli.process_input("ping"))

    def test_command_processing(self):
        @self.cli.command
        def test():
            return "done"

        self.assertFalse(self.cli.was_processed())
        self.assertEqual("done", self.cli.process_input("test"))
        self.assertTrue(self.cli.was_processed())

        self.cli.process_input("aaaa")
        self.assertFalse(self.cli.was_processed())




if __name__ == '__main__':
    unittest.main()
