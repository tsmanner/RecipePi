""" Unit Tests for recipepi.htmlrender.HTMLTag
"""
import unittest
from recipepi.renderhtml import HTMLTag


class TestHTMLTag(unittest.TestCase):
    def test_open(self):
        tag = HTMLTag("test")
        with self.subTest("No Attributes"):
            self.assertEqual(tag.open(), "<test>")
        with self.subTest("With Attributes"):
            tag.attributes["key"] = "value"
            self.assertEqual(tag.open(), '<test key="value">')

    def test_close(self):
        tag = HTMLTag("test")
        self.assertEqual(tag.close(), '</test>')

    def test_render(self):
        tag = HTMLTag("test")
        with self.subTest("No Attributes"):
            self.assertEqual(tag.render(), '<test></test>')
        with self.subTest("With Attributes"):
            tag.attributes["key"] = "value"
            self.assertEqual(tag.render(), '<test key="value"></test>')
