""" Recipe
"""
from typing import Iterable, Union
from recipepi.graph import Graph, Node, NodeGroup, connect
from recipepi.renderhtml import HTMLTable, HTMLRow, HTMLCell


class Ingredient(Node):
    def __init__(self, recipe: "Recipe", name):
        super().__init__(recipe)
        self.name = name

    def graphviz(self):
        return '"{}" [shape=rectangle color=gray fontcolor=gray label="{}"]'.format(self.id, self.name)

    def __repr__(self):
        return "Ingredient({})".format(self.name)

    def __str__(self):
        return self.name


class Amount(Node):
    def __init__(self, recipe: "Recipe", amount: Union[str, int], modifies: Node = None):
        super().__init__(recipe)
        self.amount = amount
        if modifies:
            connect(modifies, self)

    def graphviz(self):
        return '"{}" [shape=rectangle color=gray fontcolor=gray label="{}"]'.format(self.id, self.amount)

    def __repr__(self):
        return "Amount({})".format(self.amount)

    def __str__(self):
        return str(self.amount)


class Step(Node):
    def __init__(self, recipe: "Recipe", procedure):
        super().__init__(recipe)
        self.procedure = procedure

    def graphviz(self):
        return '"{}" [shape=rectangle color=gray fontcolor=gray label="{}"]'.format(self.id, self.procedure)

    def __repr__(self):
        return "Step({})".format(self.procedure)

    def __str__(self):
        return self.procedure


class Recipe(Graph):
    def __init__(self, name: str):
        super().__init__(name)

    def __repr__(self):
        lines = [
            'Recipe: {}'.format(self.name),
        ]
        for node in self.nodes:
            lines.append('{}'.format(node))
        edges = set()
        for tail in self.nodes:
            for head in tail.outgoing:
                edges.add((tail.id, head.id))
        for edge in sorted(edges):
            lines.append('{} -> {}'.format(*edge))
        return "\n    ".join(lines)

    def ingredient(self, name, amount):
        ingredient = Ingredient(self, name)
        amount = Amount(self, amount, ingredient)
        return NodeGroup(ingredient, amount)

    def step(self, procedure, *inputs):
        step = Step(self, procedure)
        for ipt in inputs:
            if isinstance(ipt, Iterable):
                [connect(item, step) for item in ipt]
            else:
                connect(ipt, step)
        return step

    def render_html(self):
        cells = {node: HTMLCell(node) for node in self.nodes}
        columns = []
        for node in self.nodes:
            column = get_column_for_node(node)
            cells[node].column = column
            cells[node].rowspan = get_rowspan_for_node(node)
            if cells[node].rowspan > 1:
                cells[node].attributes["rowspan"] = cells[node].rowspan
            while column >= len(columns):
                columns.append([])
            columns[column].append(node)
        calculate_rows(columns[-1], 0, cells)
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
        # Do some formatting
        table.attributes["style"] = "border-spacing: 0;"
        # Render the HTML
        # with open("rawr.html", "w") as f:
        #     f.write(table.render())
        return table.render()


def get_column_for_node(node):
    if isinstance(node, Step):
        return node.depth("up") - 1
    if isinstance(node, Amount):
        return max([get_column_for_node(item) for item in node.incoming]) + 1
    if isinstance(node, Ingredient):
        return 0
    raise TypeError(
        "get_column_for_node must be called on Step, Amount, or Ingredient, not {}".format(type(node).__name__)
    )


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


def parse_recipe(recipe_text):
    """ Parse the recipe text, returning a Recipe object
    """
    print("Parsing:")
    print(recipe_text)
    r = Recipe("Tom's Chili")
    meats = NodeGroup()
    meats += r.ingredient("Ground Beef", "1/2 Lb")
    meats += r.ingredient("Ground Pork", "1/4 Lb")
    meats += r.ingredient("Ground Veal", "1/4 Lb")
    meats += r.ingredient("Water", "1/2 Cup")

    ptoo = NodeGroup()
    ptoo += r.ingredient("Plum Tomato", "2")
    ptoo += r.ingredient("Olive Oil", "1/4 Cup")

    veggies = NodeGroup()
    veggies += r.ingredient("Red Bell Peper", "1")
    veggies += r.ingredient("Orange Bell Pepper", "1")
    veggies += r.ingredient("Mild Pepper", "1")
    veggies += r.ingredient("Yellow Onion", "2")
    veggies += r.ingredient("Garlic", "1/2 Head")

    cans = NodeGroup()
    cans += r.ingredient("Black Beans", "1 Can")
    cans += r.ingredient("Kidney Beans", "1 Can")
    cans += r.ingredient("Sweet Corn", "1 Can")

    seasonings = NodeGroup()
    seasonings += r.ingredient("Chili Powder", "3 Tbsp")
    seasonings += r.ingredient("Basil Powder", "3 Tbsp")
    seasonings += r.ingredient("Paprika", "1 Tsp")
    seasonings += r.ingredient("Cayenne Powder", "1 Tsp")
    seasonings += r.ingredient("Salt", "To Taste")

    meat_mix = r.step("Mix in pot over medium heat and brown", meats)
    puree = r.step("Puree", ptoo)
    dice = r.step("Dice", veggies)
    veggie_mix = r.step("Combine and simmer for 30 minutes or until vegetables soften", meat_mix, puree, dice)
    drain = r.step("Open, draining most of the fluid", cans)
    mix = r.step(
        "Mix in pot and simmer for at least another 30 minutes.  Longer is typically better",
        seasonings,
        veggie_mix,
        drain,
    )
    return r
