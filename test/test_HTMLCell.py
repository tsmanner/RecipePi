""" Unit Tests for recipepi.htmlrender.HTMLCell
"""
import unittest
from recipepi.renderhtml import HTMLCell


class TestHTMLCell(unittest.TestCase):
    def test_body(self):
        cell = HTMLCell("test")
        self.assertEqual(cell.body(), 'test')

    def test_render(self):
        cell = HTMLCell("test")
        self.assertEqual(cell.render(), '<td>test</td>')
