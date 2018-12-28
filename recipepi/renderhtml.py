""" HTML Rendering classes and functions
"""

from typing import List


class HTMLTag:
    def __init__(self, tag):
        self.tag = tag
        self.attributes = {}

    def open(self):
        s = '<{}'.format(self.tag)
        for k, v in self.attributes.items():
            s += ' {}="{}"'.format(k, v)
        s += '>'
        return s

    def body(self):
        return ''

    def close(self):
        return '</{}>'.format(self.tag)

    def render(self):
        return '{}{}{}'.format(self.open(), self.body(), self.close())


class HTMLTable(HTMLTag):
    def __init__(self):
        super().__init__('table')
        self.rows = []  # type: List[HTMLRow]
        self.row_type = HTMLRow

    @property
    def num_rows(self):
        return len(self.rows)

    @property
    def num_cols(self):
        return max([len(row) for row in self.rows])

    def column(self, col):
        cells = []
        for row in self.rows:
            current_column = 0
            for cell in row.cells:
                max_col = current_column + (cell.attributes["colspan"] - 1 if "colspan" in cell.attributes else 0)
                if current_column <= col <= max_col:
                    cells.append(cell)
                current_column += cell.attributes["colspan"] if "colspan" in cell.attributes else 1
        return cells

    def __getitem__(self, item):
        if not isinstance(item, int):
            raise TypeError(
                "{} indices must be integers or slices, not {}".format(type(self).__name__, type(item).__name__)
            )
        while item >= len(self.rows):
            self.rows.append(self.row_type())
        return self.rows[item]

    def __setitem__(self, key, value):
        if not isinstance(key, int):
            raise TypeError(
                "{} indices must be integers or slices, not {}".format(type(self).__name__, type(key).__name__)
            )
        if not isinstance(value, self.row_type):
            raise TypeError(
                "{} values must be {}, not {}".format(
                    type(self).__name__,
                    self.row_type.__name__,
                    type(key).__name__,
                )
            )
        while key >= len(self.rows):
            self.rows.append(self.row_type())
        self.rows[key] = value

    def body(self):
        return ''.join([row.render() for row in self.rows])


class HTMLRow(HTMLTag):
    def __init__(self, content: List = None):
        super().__init__('tr')
        self.cells = []  # type: List[HTMLCell]
        self.cell_type = HTMLCell
        if content:
            [self.append(item) for item in content]

    def __getitem__(self, item):
        if not isinstance(item, int):
            raise TypeError(
                "{} indices must be integers or slices, not {}".format(type(self).__name__, type(item).__name__)
            )
        while item >= len(self.cells):
            self.cells.append(self.cell_type())
        return self.cells[item]

    def __setitem__(self, key, value):
        if not isinstance(key, int):
            raise TypeError(
                "{} indices must be integers or slices, not {}".format(type(self).__name__, type(key).__name__)
            )
        while key >= len(self.cells):
            self.cells.append(self.cell_type())
        if not isinstance(value, self.cell_type):
            cell = self[key]
            cell.content = value
        else:
            self.cells[key] = value

    def __len__(self):
        return len(self.cells)

    def append(self, item):
        self.__setitem__(len(self), item)

    def body(self):
        return ''.join([cell.render() for cell in self.cells])


class HTMLCell(HTMLTag):
    def __init__(self, content=''):
        super().__init__('td')
        self.content = content
        self.border = {
            "top": False,
            "bottom": False,
            "left": False,
            "right": False,
            "size": "1px",
            "type": "solid",
            "color": "black",
        }

    def open(self):
        # Capture the user style string
        user_style = self.attributes["style"] if "style" in self.attributes else ""
        # Create a new style string, and prepend on the calculated borders
        calculated_border_style = ''
        for edge in ["top", "bottom", "left", "right"]:
            if self.border[edge]:
                calculated_border_style += "border-{}: {} {} {};".format(
                    edge,
                    self.border["size"],
                    self.border["type"],
                    self.border["color"]
                )
        calculated_border_style += user_style
        # Set the style attribute, generate the open tag string, and then reset it back to the user's before returning
        self.attributes["style"] = calculated_border_style
        open_string = super().open()
        if user_style != "":
            self.attributes["style"] = user_style
        else:
            del self.attributes["style"]
        return open_string

    def body(self):
        return self.content
