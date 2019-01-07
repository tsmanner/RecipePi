""" Unit Tests for recipepi.htmlrender.HTMLRow
"""
import unittest
from recipepi.renderers.html import HTMLTable, HTMLDataCell


class TestHTMLTable(unittest.TestCase):
    def test___getitem__(self):
        with self.subTest("In Range"):
            table = HTMLTable()
            item = HTMLDataCell("rawr")
            dict.__setitem__(table, 0, item)
            self.assertEqual(table[0], item)
        # with self.subTest("Out of Range"):
        #     table = HTMLTable()
        #     row = table[0]
        #     self.assertTrue(isinstance(row, table.row_type))

    # def test___setitem__(self):
    #     with self.subTest("New Item"):
    #         table = HTMLTable()
    #         row = HTMLRow()
    #         table[0] = row
    #         self.assertEqual(table[0], row)
    #     with self.subTest("Existing Item"):
    #         table = HTMLTable()
    #         old_row = HTMLRow()
    #         table[0] = old_row
    #         self.assertEqual(table[0], old_row)
    #         new_row = HTMLRow()
    #         table[0] = new_row
    #         self.assertEqual(table[0], new_row)
    #     with self.subTest("Extension"):
    #         table = HTMLTable()
    #         row_1 = HTMLRow()
    #         table[1] = row_1
    #         self.assertEqual(table[0].cells, [])  # An empty row
    #         self.assertEqual(table[1], row_1)
    #
    # def test_body(self):
    #     with self.subTest("Empty"):
    #         table = HTMLTable()
    #         self.assertEqual(table.body(), '')
    #     with self.subTest("Non-Empty"):
    #         table = HTMLTable()
    #         table.rows.append(HTMLRow())
    #         self.assertEqual(table.body(), '<tr></tr>')

    def test_render(self):
        with self.subTest("With Attributes"):
            table = HTMLTable()
            table.attributes["key"] = "value"
            self.assertEqual(table.render(), '<table key="value"></table>')
        with self.subTest("Without Attributes"):
            table = HTMLTable()
            self.assertEqual(table.render(), '<table></table>')

