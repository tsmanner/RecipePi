from typing import Iterable

from recipepi.recipe.graph import Graph, Node, NodeGroup, connect
from recipepi.recipe.amount import Amount
from recipepi.recipe.ingredient import Ingredient
from recipepi.recipe.step import Step


class Recipe(Graph):
    class EndNode(Node):
        def __init__(self, recipe):
            super().__init__(recipe)

        def graphviz(self):
            return None

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

