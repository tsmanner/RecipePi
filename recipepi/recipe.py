""" Recipe
"""
from functools import lru_cache
import os


def svg(item, *args, **kwargs):
    return item.__svg__(*args, **kwargs)


def _get_id():
    current_id = 0
    while True:
        current_id += 1
        yield current_id


ID = _get_id()


class Recipe:
    def __init__(self, name):
        self.name = name
        self.ingredients = set()
        self.steps = set()
        self.edges = set()

    def connect(self, tail, head):
        self.add(tail)
        self.add(head)
        self.add(Edge(tail, head))

    def add(self, element):
        if isinstance(element, Ingredient):
            self.ingredients.add(element)
        elif isinstance(element, Step):
            self.steps.add(element)
        elif isinstance(element, Edge):
            self.edges.add(element)

    def graphviz(self, linesep='\n'):
        lines = [
            'digraph "{}" {{'.format(self.name),
            '    label="{}"'.format(self.name.capitalize()),
            '    labelloc=t',
            '    fontsize=24',
            '    rankdir=LR',
            '    bgcolor=black',
        ] + [
            '    ' + graphviz(recipe_element)
            for recipe_element in sorted(self.ingredients | self.steps | self.edges)
        ] + [
            '}'
        ]
        return linesep.join(lines)


@lru_cache()
def get_recipe(recipe_name):
    return Recipe(recipe_name)


class Node(dict):
    def __init__(self, recipe: Recipe):
        super().__init__()
        self.id = next(ID)
        self["recipe"] = recipe
        self["id"] = self.id
        self["edges"] = set()
        self["format"] = "Node({id})"
        self["graphviz_format"] = '"{id}" [label="Node({id})"]'
        recipe.add(self)

    def __lt__(self, other):
        return self.id < other.id

    def __hash__(self):
        return self.id

    def __str__(self):
        return self["format"].format(**self)


class Edge(dict):
    def __init__(self, tail: "Node", head: "Node"):
        super().__init__()
        self.id = next(ID)
        self.tail = tail
        self["tail"] = tail.id
        tail["edges"].add(self)
        self.head = head
        self["head"] = head.id
        head["edges"].add(self)
        self["graphviz_format"] = '"{tail}" -> "{head}" [color=gray]'

    def __lt__(self, other):
        return self.id < other.id

    def __hash__(self):
        return self.id

    def __str__(self):
        return " -> "


class Ingredient(Node):
    def __init__(self, recipe, name, amount):
        super().__init__(recipe)
        self["name"] = name
        self["amount"] = amount
        self["graphviz_format"] = '"{id}" [color=gray fontcolor=gray shape=rectangle label="{name} {amount}"]'


class Step(Node):
    def __init__(self, recipe, procedure, *inputs):
        super().__init__(recipe)
        self["procedure"] = procedure
        self["graphviz_format"] = '"{id}" [color=gray fontcolor=gray shape=rectangle label="{procedure}"]'
        [recipe.connect(item, self) for item in inputs]


def graphviz(element):
    return element["graphviz_format"].format(**element)


if __name__ == '__main__':
    import subprocess as sp
    r = get_recipe("Tom's Chili")
    gb = Ingredient(r, "Ground Beef", "1/2 Lb")
    gp = Ingredient(r, "Ground Pork", "1/4 Lb")
    gv = Ingredient(r, "Ground Veal", "1/4 Lb")
    w = Ingredient(r, "Water", "1/2 Cup")

    pt = Ingredient(r, "Plum Tomato", "2")
    oo = Ingredient(r, "Olive Oil", "1/4 Cup")

    rbp = Ingredient(r, "Red Bell Peper", "1")
    obp = Ingredient(r, "Orange Bell Pepper", "1")
    mp = Ingredient(r, "Mild Pepper", "1")
    yo = Ingredient(r, "Yellow Onion", "2")
    g = Ingredient(r, "Garlic", "1/2 Head")

    black_beans = Ingredient(r, "Black Beans", "1 Can")
    kidney_beans = Ingredient(r, "Kidney Beans", "1 Can")
    corn = Ingredient(r, "Sweet Corn", "1 Can")

    chili_powder = Ingredient(r, "Chili Powder", "3 Tbsp")
    basil_powder = Ingredient(r, "Basil Powder", "3 Tbsp")
    paprika = Ingredient(r, "Paprika", "1 Tsp")
    cayenne_powder = Ingredient(r, "Cayenne Powder", "1 Tsp")
    salt = Ingredient(r, "Salt", "To Taste")

    meat_mix = Step(r, "Mix in pot over medium heat and brown", gb, gp, gv, w)
    puree = Step(r, "Puree", pt, oo)
    dice = Step(r, "Dice", rbp, obp, mp, yo, g)
    veggie_mix = Step(r, "Combine and simmer for 30 minutes or until vegetables soften", meat_mix, puree, dice)
    drain = Step(r, "Open, draining most of the fluid", black_beans, kidney_beans, corn)
    mix = Step(
        r,
        "Mix in pot and simmer for at least another 30 minutes.  Longer is typically better",
        chili_powder,
        basil_powder,
        paprika,
        cayenne_powder,
        salt,
        veggie_mix,
        drain,
    )

    print(r.graphviz())
    with open("rawr.dot", "w") as dotfile:
        dotfile.write(r.graphviz())
    sp.run('dot -Tpng -o rawr.png rawr.dot', shell=True)
