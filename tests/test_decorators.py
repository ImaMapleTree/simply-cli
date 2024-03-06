import unittest

from simplycli.decorators import description


class DescriptionDecoratorTest(unittest.TestCase):
    @description("Test description")
    def method_annotated_with_description(self):
        return 100

    @description("Test description")
    class ClassAnnotatedWithDescription:
        def __init__(self, value):
            self.value = value

    @staticmethod
    def create_invalid_annotated_method():
        @description
        def invalid_method():
            return 0

    # tests if the annotated method both works and that its __description__ property is properly set
    def test_valid_annotated_method(self):
        self.assertEqual(100, self.method_annotated_with_description())
        desc = self.method_annotated_with_description.__description__
        self.assertEqual("Test description", desc)

    def test_valid_annotated_class(self):
        cls = DescriptionDecoratorTest.ClassAnnotatedWithDescription("test value")
        self.assertEqual("test value", cls.value)
        self.assertEqual("Test description", cls.__description__)

    # tests if creating a method with @description and no value raises an exception
    def test_invalid_annotated_method(self):
        self.assertRaises(ValueError, self.create_invalid_annotated_method)


if __name__ == '__main__':
    unittest.main()
