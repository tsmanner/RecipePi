from typing import Union

from recipepi.recipe.graph import Node, connect


class Amount(Node):
    def __init__(self, recipe, amount: Union[str, int], modifies: Node = None):
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
