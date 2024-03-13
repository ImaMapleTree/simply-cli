# import unittest
#
# from simplycli import decorators
# from simplycli.cli import CLI
# from simplycli.decorators import description
#
#
# class SimpleWrapperClass:
#     def __init__(self, func):
#         self.func = func
#
#     def __call__(self, *args, **kwargs):
#         return self.func(*args, **kwargs)
#
#
# def create_commands(cli: CLI):
#     @wrapper()
#     @cli.command
#     def wrapped():
#         return "Wrapped!"
#
#     @wrapper()
#     @cli.command
#     def wrapped2():
#         return "Wrapped2!"
#
#     @description("Description")
#     @wrapper()
#     @cli.command
#     class Wrapped3():
#         @staticmethod
#         def __execute__():
#             return "Wrapped3!"
#
#
# class WrappingDecoratorTest(unittest.TestCase):
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.cli = CLI()
#         create_commands(self.cli)
#
#
#     def test_simple_wrapped_command(self):
#         self.assertEqual("Wrapped!", self.cli.process_input("wrapped"))
#         self.assertEqual("Wrapped2!", self.cli.process_input("wrapped2"))
#         self.assertEqual("Wrapped3!", self.cli.process_input("wrapped3"))
#         self.assertEqual("Description", self.cli.find_command("wrapped3").description)
#
#
#
#
# if __name__ == '__main__':
#     unittest.main()
