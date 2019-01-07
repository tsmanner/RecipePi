""" Unit Tests for recipepi.htmlrender.HTMLRow
"""
import unittest
from recipepi.renderers.html import HTMLRow, HTMLDataCell


class TestHTMLRow(unittest.TestCase):
    def test___getitem__(self):
        with self.subTest("In Range"):
            row = HTMLRow(["test"])
            self.assertEqual(row[0].content, "test")
        with self.subTest("Out of Range"):
            row = HTMLRow(["test"])
            self.assertEqual(row[1].content, "")  # Indicates default constructed HTMLCell

    def test___setitem__(self):
        with self.subTest("New Item"):
            row = HTMLRow()
            row[0] = "test"
            self.assertEqual(row[0].content, "test")
        with self.subTest("Existing Item"):
            row = HTMLRow(["old"])
            row[0] = "new"
            self.assertEqual(row[0].content, "new")
        with self.subTest("Extension"):
            row = HTMLRow()
            row[1] = "test"
            self.assertEqual(len(row.cells), 2)
            self.assertEqual(row[0].content, "")
            self.assertEqual(row[1].content, "test")

    def test___len__(self):
        row = HTMLRow()
        self.assertEqual(len(row), 0)
        row.cells.append(HTMLDataCell())
        self.assertEqual(len(row), 1)

    def test_append(self):
        row = HTMLRow()
        row.append("test")
        self.assertEqual(row[0].content, "test")
        self.assertEqual(len(row.cells), 1)

    def test_body(self):
        with self.subTest("Empty"):
            row = HTMLRow()
            self.assertEqual(row.body(), '')
        with self.subTest("Non-Empty"):
            row = HTMLRow(["test"])
            self.assertEqual(row.body(), '<td style="padding: 0.2em 0.4em; margin: 0;">test</td>')

    def test_render(self):
        with self.subTest("With Attributes"):
            row = HTMLRow()
            row.attributes["key"] = "value"
            self.assertEqual(row.render(), '<tr key="value"></tr>')
        with self.subTest("Without Attributes"):
            row = HTMLRow()
            self.assertEqual(row.render(), '<tr></tr>')
