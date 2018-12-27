""" Recipe
"""
from typing import Iterable, Union
from graph import Graph, Node, NodeGroup, connect


class Ingredient(Node):
    def __init__(self, recipe: "Recipe", name):
        super().__init__(recipe)
        self.name = name

    def graphviz(self):
        return '"{}" [shape=rectangle color=gray fontcolor=gray label="{}"]'.format(self.id, self.name)

    def __repr__(self):
        return "Ingredient({})".format(self.name)


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


class Step(Node):
    def __init__(self, recipe: "Recipe", procedure):
        super().__init__(recipe)
        self.procedure = procedure

    def graphviz(self):
        return '"{}" [shape=rectangle color=gray fontcolor=gray label="{}"]'.format(self.id, self.procedure)

    def __repr__(self):
        return "Step({})".format(self.procedure)


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


if __name__ == '__main__':
    import subprocess as sp
    r = Recipe("Tom's Chili")
    meats = NodeGroup()
    meats += r.ingredient("Ground Beef", "1/2 Lb")
    meats += r.ingredient("Ground Pork", "1/4 Lb")
    meats += r.ingredient("Ground Veal", "1/4 Lb")
    meats += r.ingredient("Water", "1/2 Cup")
    print(meats)

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

    with open("rawr.dot", "w") as dotfile:
        dotfile.write(r.graphviz())
    sp.run('dot -Tpng -o rawr.png rawr.dot', shell=True)

    print(r)
