from recipepi.recipe.graph import Node


class Ingredient(Node):
    def __init__(self, recipe, name):
        super().__init__(recipe)
        self.name = name

    def graphviz(self):
        return '"{}" [shape=rectangle color=gray fontcolor=gray label="{}"]'.format(self.id, self.name)

    def __repr__(self):
        return "Ingredient({})".format(self.name)

    def __str__(self):
        return self.name
