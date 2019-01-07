""" Unit Tests for recipepi.htmlrender.HTMLCell
"""
import unittest
from recipepi.renderers.html import HTMLDataCell


class TestHTMLCell(unittest.TestCase):
    def test_body(self):
        cell = HTMLDataCell("test")
        self.assertEqual(cell.body(), 'test')

    def test_render(self):
        cell = HTMLDataCell("test")
        self.assertEqual(cell.render(), '<td style="padding: 0.2em 0.4em; margin: 0;">test</td>')
