from copy import deepcopy
from typing import List, Set, Union

from recipepi.recipe.amount import Amount
from recipepi.recipe.graph import connect
from recipepi.recipe.ingredient import Ingredient
from recipepi.recipe.recipe import Recipe
from recipepi.recipe.step import Step


class HTMLTag:
    def __init__(self, tag):
        self.tag = tag
        self.attributes = {}

    def copy(self, other=None):
        the_copy = other if other is not None else type(self)(self.tag)
        # Have to copy init arguments because we can't guarantee that
        # a constructor was called with the right stuff.  (other != None case)
        the_copy.tag = self.tag
        the_copy.attributes = self.attributes.copy()
        return the_copy

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

    def pre_render_table(self):
        pass

    def render(self):
        return '{}{}{}'.format(self.open(), self.body(), self.close())

    def post_render_table(self):
        pass


class HTMLTable(HTMLTag, dict):
    class Coordinate:
        def __init__(self, row, column):
            self.row = row
            self.col = column

        def __hash__(self):
            return self.row << 32 | self.col

        def __eq__(self, other):
            return self.row == other.row and self.col == other.col

        def __repr__(self):
            return 'HTMLTable.Coordinate(row={}, col={})'.format(self.row, self.col)

        def __str__(self):
            return '({}, {})'.format(self.row, self.col)

    class CoordinateRange:
        def __init__(self, start: "HTMLTable.Coordinate", end: "HTMLTable.Coordinate" = None):
            # If only start is provided, go from 0, 0 to it
            if end is None:
                end = start
                start = HTMLTable.Coordinate(0, 0)
            if isinstance(start, tuple) and len(start) == 2:
                start = HTMLTable.Coordinate(*start)
            if isinstance(end, tuple) and len(end) == 2:
                end = HTMLTable.Coordinate(*end)
            self.start = start
            self.end = end

        def __iter__(self):
            for row in range(self.start.row, self.end.row+1):
                for col in range(self.start.col, self.end.col+1):
                    yield HTMLTable.Coordinate(row, col)

        def __repr__(self):
            return 'HTMLTable.CoordinateRange({} -> {})'.format(self.start, self.end)

        def __str__(self):
            return '({}:{}, {}:{})'.format(
                self.start.row,
                self.end.row,
                self.start.col,
                self.end.col
            )

    class IndexPartial:
        """
        Simple partial-style object that is returned if only a row is given,
        it is how `table[row][column]` is supported.
        """
        def __init__(self, table, row):
            self.table = table
            self.row = row

        def __getitem__(self, column):
            return self.table[HTMLTable.Coordinate(self.row, column)]

        def __setitem__(self, column, value):
            self.table[HTMLTable.Coordinate(self.row, column)] = value

    def __init__(self):
        super().__init__('table')
        self._num_rows = 0
        self._num_cols = 0

    def copy(self, other=None):
        the_copy = other if other is not None else type(self)()
        HTMLTag.copy(self, the_copy)  # Copy over the HTMLTag attributes
        the_copy._num_rows = self._num_rows
        the_copy._num_cols = self._num_cols
        for coordinate, cell in self.items():
            if isinstance(cell, HTMLDataCell):
                new_cell = cell.copy()
                the_copy[coordinate] = new_cell
        return the_copy

    @property
    def num_rows(self):
        return self._num_rows

    @num_rows.setter
    def num_rows(self, rows):
        if rows > self._num_rows:
            self._num_rows = rows
            self.fill_empty_cells()

    @property
    def num_cols(self):
        return self._num_cols

    @num_cols.setter
    def num_cols(self, cols):
        if cols > self._num_rows:
            self._num_cols = cols
            self.fill_empty_cells()

    def column(self, column):
        for item in sorted(filter(lambda c: c.col == column, self), key=lambda c: c.row):
            yield self[item]

    col = column

    def row(self, row):
        for item in sorted(filter(lambda c: c.row == row, self), key=lambda c: c.col):
            yield self[item]

    def fill_empty_cells(self):
        """
        Accessing an empty coordinate will create an `EmptyCell`
        instance there, so just touch everything
        """
        for _ in self.values():
            pass

    def collapse_borders(self, coord_range: "HTMLTable.CoordinateRange" = None):
        if coord_range is None:
            coord_range = self.CoordinateRange((self.num_rows-1, self.num_cols-1))
        for coordinate in coord_range:
            self[coordinate].collapse_borders = True

    def insert_table(self, coordinate: "HTMLTable.Coordinate", table: "HTMLTable", displace: str):
        """
        1. Make a copy of self,
        2. Displace cells that would fall in the new table's range ('right' or 'down')
        3. Insert the new cells
        4. Return the copy
        """
        new_table = self.copy()
        cells_to_displace = set()  # type: Set[Union[HTMLDataCell, HTMLDataCell.Shadow]]
        for row in reversed(range(new_table.num_rows)):
            for col in reversed(range(new_table.num_cols)):
                current_coordinate = new_table.Coordinate(row, col)
                affecting_row = coordinate.row <= row <= coordinate.row + table.num_rows
                affecting_col = coordinate.col <= col <= coordinate.col + table.num_cols
                displaced_cell = new_table[current_coordinate]
                if isinstance(displaced_cell, HTMLDataCell.Shadow):
                    displaced_cell = displaced_cell.cell
                if isinstance(displaced_cell, HTMLDataCell):
                    # Do 'right' displacement if we're on a row that will be affected
                    if displace == 'right' and affecting_row:
                        cells_to_displace.add(displaced_cell)
                    # Do 'down' displacement if we're on a column that will be affected
                    elif displace == 'down' and affecting_col:
                        cells_to_displace.add(displaced_cell)

        for cell in cells_to_displace:
            if displace == 'right':
                displace_coordinate = new_table.Coordinate(
                    cell.coordinate.row,
                    cell.coordinate.col + table.num_cols
                )
            elif displace == 'down':
                displace_coordinate = new_table.Coordinate(
                    cell.coordinate.row + table.num_rows,
                    cell.coordinate.col
                )
            else:
                raise ValueError(
                    "displace must be either 'right' or 'down', not '{}'".format(displace)
                )
            # print('  {} -> {}'.format(cell.coordinate, displace_coordinate))
            new_table[cell.coordinate] = EmptyCell()
            new_table[displace_coordinate] = cell

        for row in reversed(range(max(new_table.num_rows, coordinate.row + table.num_rows))):
            for col in reversed(range(max(new_table.num_cols, coordinate.col + table.num_cols))):
                current_coordinate = new_table.Coordinate(row, col)
                affecting_row = coordinate.row <= row <= coordinate.row + table.num_rows
                affecting_col = coordinate.col <= col <= coordinate.col + table.num_cols
                if affecting_row and affecting_col:
                    source_coordinate = table.Coordinate(
                        row - coordinate.row,
                        col - coordinate.col
                    )
                    if source_coordinate in table:
                        new_table[current_coordinate] = table[source_coordinate]
        return new_table

    def __contains__(self, item):
        if isinstance(item, HTMLTable.Coordinate):
            return item.row < self.num_rows and item.col < self.num_cols
        raise ValueError(
            "{} can only contain HTMLTable.Coordinate keys, not {}".format(
                type(self).__name__,
                type(item).__name__
            )
        )

    def __getitem__(self, item):
        if isinstance(item, int):
            return HTMLTable.IndexPartial(self, item)
        elif isinstance(item, tuple) and len(item) == 2 and isinstance(item[0], int) and isinstance(item[1], int):
            return self[HTMLTable.Coordinate(*item)]
        elif isinstance(item, HTMLTable.Coordinate):
            if not super().__contains__(item):
                self[item] = EmptyCell()
            return super().__getitem__(item)
        else:
            raise TypeError(
                "{} indices must be int, HTMLTableCoordinate, or Tuple[int, int], not {}".format(
                    type(self).__name__,
                    type(item).__name__
                )
            )

    def __setitem__(self, key, value: Union["HTMLDataCell", "HTMLDataCell.Shadow", "EmptyCell"]):
        if isinstance(key, tuple) and len(key) == 2 and isinstance(key[0], int) and isinstance(key[1], int):
            self[HTMLTable.Coordinate(*key)] = value
        elif isinstance(key, HTMLTable.Coordinate):
            if isinstance(value, HTMLDataCell):
                value.table = self
                value.coordinate = key
                self._num_rows = max(self._num_rows, key.row+1)
                self._num_cols = max(self._num_cols, key.col+1)
                super().__setitem__(key, value)
                value.expand()
            elif isinstance(value, HTMLDataCell.Shadow):
                value.coordinate = key
                self._num_rows = max(self._num_rows, key.row+1)
                self._num_cols = max(self._num_cols, key.col+1)
                super().__setitem__(key, value)
            elif isinstance(value, EmptyCell):
                value.table = self
                value.coordinate = key
                self._num_rows = max(self._num_rows, key.row+1)
                self._num_cols = max(self._num_cols, key.col+1)
                super().__setitem__(key, value)
            else:
                raise TypeError(
                    '{} values must be HTMLCell, HTMLCell.Shadow, or EmptyCell not {}'.format(
                        type(self).__name__,
                        type(value).__name__
                    )
                )
        else:
            raise TypeError(
                '{} indices must be HTMLTable.Coordinate or Tuple[int, int], not {}'.format(
                    type(self).__name__,
                    type(key).__name__
                )
            )

    def dump(self):
        lines = []
        column_widths = [0] * self.num_cols
        tokens = []  # type: List[List[Union[int, str]]]
        for row in range(self.num_rows):
            tokens.append([row])
            for col in range(self.num_cols):
                coordinate = HTMLTable.Coordinate(row, col)
                tokens[-1].append(str(self[coordinate]))
                column_widths[col] = max(column_widths[col], len(tokens[-1][-1]))
        column_widths.insert(0, 4)  # The row number should be 4 wide
        line_format = (' {{:>{}}} |' * (len(column_widths))).format(*column_widths)
        lines.append(line_format.format('', *[col for col in range(self.num_cols)]))
        for line_tokens in tokens:
            lines.append(line_format.format(*line_tokens))
        return '\n'.join(lines)

    def body(self):
        rows = [HTMLRow([self[row][col] for col in range(self.num_cols)]) for row in range(self.num_rows)]
        return ''.join([row.render() for row in rows])

    def keys(self):
        for row in range(self.num_rows):
            for col in range(self.num_cols):
                yield self.Coordinate(row, col)

    def values(self):
        for coordinate in self.keys():
            yield self[coordinate]

    def items(self):
        for coordinate in self.keys():
            yield coordinate, self[coordinate]

    def rows(self):
        for row in range(self.num_rows):
            yield self.row(row)

    def cols(self):
        for col in range(self.num_cols):
            yield self.column(col)

    def __iter__(self):
        return self.keys()

    def pre_render_table(self):
        for cell in self.values():
            cell.pre_render_table()

    def render(self):
        self.pre_render_table()
        rendered_table = super().render()
        self.post_render_table()
        return rendered_table

    def post_render_table(self):
        for cell in self.values():
            cell.post_render_table()


class HTMLRow(HTMLTag, list):
    def __init__(self, *args):
        HTMLTag.__init__(self, 'tr')
        list.__init__(self, *args)

    def copy(self, other=None):
        the_copy = other if other is not None else type(self)()
        HTMLTag.copy(self, the_copy)  # Copy over the HTMLTag attributes
        [the_copy.append(item.copy()) for item in self]
        return the_copy

    def body(self):
        tokens = []
        for item in self:
            if item:
                tokens.append(item.render())
            else:
                tokens.append('<td></td>')
        return ''.join(tokens)


class HTMLCell(HTMLTag):
    def __init__(self):
        super().__init__('td')
        self.table = None  # type: HTMLTable
        self.coordinate = None  # type: HTMLTable.Coordinate
        self.collapse_borders = False
        self.border = {
            "top": False,
            "bottom": False,
            "left": False,
            "right": False,
            "size": "1px",
            "type": "solid",
            "color": "#a2a9b1",
        }
        self.rendered_border = self.border
        self.attributes["style"] = "padding: 0.2em 0.4em; margin: 0;"

    def copy(self, other=None):
        the_copy = other if other is not None else type(self)()
        HTMLTag.copy(self, the_copy)  # Copy over the HTMLTag attributes
        # Don't copy the table, a copied cell shouldn't think that it is in a table
        the_copy.coordinate = self.coordinate  # Do let it know where it used to be
        the_copy.border = self.border.copy()
        return the_copy

    def negotiate_border(self, direction):
        direction_map = {
            'left': 'right',
            'right': 'left',
            'top': 'bottom',
            'bottom': 'top'
        }
        coordinate_step_fns = {
            'left': lambda c: HTMLTable.Coordinate(c.row, c.col-1),
            'right': lambda c: HTMLTable.Coordinate(c.row, c.col+1),
            'top': lambda c: HTMLTable.Coordinate(c.row-1, c.col),
            'bottom': lambda c: HTMLTable.Coordinate(c.row+1, c.col)
        }
        coordinate = coordinate_step_fns[direction](self.coordinate)
        if coordinate not in self.table:
            return
        neighbor = self.table[coordinate]
        while isinstance(neighbor, HTMLDataCell.Shadow) and neighbor.cell is self:
            coordinate = coordinate_step_fns[direction](coordinate)
            if coordinate not in self.table:
                return
            neighbor = self.table[coordinate]
        if self.rendered_border[direction] and neighbor and neighbor.rendered_border and\
                neighbor.rendered_border[direction_map[direction]] and neighbor.rowspan >= self.rowspan:
            self.rendered_border[direction] = False

    def pre_render_table(self):
        """ Collapse the borders only if we are in a table and know where
            Start the rendered borders as the borders we want.
        """
        self.rendered_border = self.border
        if self.collapse_borders:
            self.negotiate_border("left")
            self.negotiate_border("right")
            self.negotiate_border("top")
            self.negotiate_border("bottom")

    def open(self):
        # Capture the user style string
        user_style = self.attributes["style"] if "style" in self.attributes else ""
        # Create a new style string, and prepend on the calculated borders
        calculated_border_style = ''
        for edge in ["top", "bottom", "left", "right"]:
            if self.rendered_border[edge]:
                calculated_border_style += "border-{}: {} {} {};".format(
                    edge,
                    self.rendered_border["size"],
                    self.rendered_border["type"],
                    self.rendered_border["color"]
                )
        # Set the style attribute, generate the open tag string, and then reset it back to the user's before returning
        self.attributes["style"] = calculated_border_style + user_style
        open_string = super().open()
        if user_style != "":
            self.attributes["style"] = user_style
        else:
            del self.attributes["style"]
        return open_string

    def post_render_table(self):
        self.rendered_border = None


class HTMLDataCell(HTMLCell):
    class Shadow(object):
        def __init__(self, cell, coordinate):
            self.cell = cell
            self.coordinate = coordinate
            self.cell.shadows.add(self)

        def copy(self, other=None):
            raise NotImplementedError("HTMLDataCell.Shadow objects should not be copied!")

        def __str__(self):
            return 'Shadow{}'.format(self.cell)

        def __setattr__(self, key, value):
            try:
                super().__setattr__(key, value)
            except:
                pass

        def __getattr__(self, item):
            return self

        def __setitem__(self, key, value):
            pass

        def __getitem__(self, item):
            return self

        def delete(self):
            if self.cell.table[self.coordinate] is self:
                del self.cell.table[self.coordinate]
            if self in self.cell.shadows:
                self.cell.shadows.remove(self)

        @property
        def rendered_border(self):
            return self.cell.border

        @property
        def rowspan(self):
            return self.cell.rowspan

        @property
        def colspan(self):
            return self.cell.colspan

        def pre_render_table(self):
            pass

        @staticmethod
        def render():
            return ''

        def post_render_table(self):
            pass

    def __init__(self, content=''):
        super().__init__()
        self.shadows = set()
        self.content = content

    def copy(self, other=None):
        the_copy = other if other is not None else type(self)(self.content)
        HTMLCell.copy(self, the_copy)  # Copy over the HTMLTag attributes
        # Don't copy the shadows, require that this cell get expanded again
        the_copy.content = self.content
        return the_copy

    def __str__(self):
        return "Cell({})".format(self.content)

    @property
    def rowspan(self):
        return self.attributes["rowspan"] if "rowspan" in self.attributes else 1

    @rowspan.setter
    def rowspan(self, value):
        self.attributes["rowspan"] = value
        self.expand()

    @property
    def colspan(self):
        return self.attributes["colspan"] if "colspan" in self.attributes else 1

    @colspan.setter
    def colspan(self, value):
        self.attributes["colspan"] = value
        self.expand()

    def clear_shadows(self):
        for shadow in list(self.shadows):
            shadow.delete()

    def expand(self):
        if not self.table:
            return
        self.clear_shadows()
        for row_offset in range(self.rowspan):
            for col_offset in range(self.colspan):
                if row_offset == col_offset == 0:
                    continue
                coordinate = HTMLTable.Coordinate(self.coordinate.row + row_offset, self.coordinate.col + col_offset)
                item = self.table[coordinate]
                if isinstance(item, EmptyCell) or item is None:
                    self.table[coordinate] = self.Shadow(self, coordinate)
                else:
                    raise KeyError(
                        "{} would be overwritten by {}._expand() into {}".format(
                            item,
                            self,
                            coordinate
                        )
                    )

    def body(self):
        return self.content


class EmptyCell(HTMLCell):
    def copy(self, other=None):
        the_copy = other if other is not None else type(self)()
        HTMLCell.copy(self, the_copy)
        return the_copy

    @property
    def content(self):
        return ''

    @property
    def rowspan(self):
        return 1

    @property
    def colspan(self):
        return 1

    def __repr__(self):
        return "-Empty-"

    def body(self):
        return self.content


def render_html(recipe: Recipe):
    return old_render_html(recipe)


def old_render_html(recipe: Recipe):
    end = Recipe.EndNode(recipe)
    cells = {node: HTMLDataCell(node) for node in recipe.nodes}
    columns = []
    for node in recipe.nodes:
        # if isinstance(node, Recipe.EndNode):
        #     continue
        if not node.outgoing and node != end:
            connect(node, end)
        column = get_column_for_node(node)
        cells[node].row = None
        cells[node].column = column
        cells[node].rowspan = get_rowspan_for_node(node)
        if cells[node].rowspan > 1:
            cells[node].attributes["rowspan"] = cells[node].rowspan
        while column >= len(columns):
            columns.append([])
        columns[column].append(node)
    calculate_rows(columns[-1], 0, cells)
    # calculate_rows_new(len(columns)-1, 0, columns, cells)
    del end
    # Populate the table
    table = HTMLTable()
    for cell in cells.values():
        table[cell.row][cell.column] = cell
    # Add padding cells for empty regions so we can get all the borders we need
    for col in range(table.num_cols):
        last_cell = table.column(col)[-1]
        for r in range(last_cell.row + (last_cell.attributes["rowspan"] if "rowspan" in last_cell.attributes else 1), table.num_rows):
            cell = table[r][col]
            cell.row = r
            cell.column = col
            cell.rowspan = 1
            set_cell_border(table, cell)
    # Setup the borders
    for cell in cells.values():
        set_cell_border(table, cell)
    for r, row in enumerate(table.rows):
        for c, cell in enumerate(row.cells):
            # if not hasattr(cell, "row"):
            #     print(r, c, cell.content)
            if isinstance(cell.content, Amount):
                cell.attributes["width"] = 75
                cell.attributes["style"] = "padding: 3;"
            elif isinstance(cell.content, Ingredient):
                cell.attributes["width"] = 150
                cell.attributes["style"] = "padding: 3;"
            elif isinstance(cell.content, Step):
                cell.attributes["width"] = 150
                cell.attributes["style"] = "padding: 3;"
    for row in table.rows:
        for cell in row.cells:
            cell.border["top"] = True
            cell.border["bottom"] = True
            cell.border["left"] = True
            cell.border["right"] = True
    # Do some formatting
    table.attributes["style"] = "border-spacing: 0;"
    # Render the HTML
    # with open("rawr.html", "w") as f:
    #     f.write(table.render())
    return table.render()


def get_column_for_node(node):
    if isinstance(node, (Step, Recipe.EndNode)):
        return node.depth("up") - 1
    if isinstance(node, Amount):
        return max([get_column_for_node(item) for item in node.incoming]) + 1
    if isinstance(node, Ingredient):
        return 0
    # if isinstance(node, Recipe.EndNode):
    #     return None
    raise TypeError(
        "get_column_for_node must be called on Step, Amount, or Ingredient, not {}".format(type(node).__name__)
    )


def set_cell_border(table, cell):
    if cell.row == 0:
        cell.border["top"] = True
    if (cell.row + cell.rowspan) == table.num_rows or \
            isinstance(cell.content, Ingredient) or\
            isinstance(cell.content, Amount) or \
            isinstance(cell.content, Step):
        cell.border["bottom"] = True
    if cell.column == 0:
        cell.border["left"] = True
    if (cell.column + 1) == table.num_cols or \
            isinstance(cell.content, Amount) or\
            isinstance(cell.content, Step):
        cell.border["right"] = True


def get_rowspan_for_node(node):
    return len([item for item in node.traverse("up") if not item.incoming])


def calculate_rows(column, current_row, cells):
    """ Sort the column by rowspan, then ID
    Key Algorithm:
        Figure out how many bits are needed to store the id
        Shift the rowspan left by that many bits and bitwise OR the two
    """
    id_offset = len('{:b}'.format(max([n.id for n in cells.keys()])))
    for node in reversed(sorted(column, key=lambda n: (get_rowspan_for_node(n) << id_offset) | n.id)):
        cell = cells[node]
        cell.row = current_row
        calculate_rows(node.incoming, current_row, cells)
        current_row += cell.rowspan


def calculate_rows_new(column_num, current_row, columns, cells):
    """ Sort the column by rowspan, then ID
    Key Algorithm:
        Figure out how many bits are needed to store the id
        Shift the rowspan left by that many bits and bitwise OR the two
    """
    column = columns[column_num]
    id_offset = len('{:b}'.format(max([n.id for n in cells.keys()])))
    for node in reversed(sorted(column, key=lambda n: (get_rowspan_for_node(n) << id_offset) | n.id)):
        cell = cells[node]
        cell.row = current_row
        if column_num > 0:
            calculate_rows(column_num-1, current_row, columns, cells)
        current_row += cell.rowspan
