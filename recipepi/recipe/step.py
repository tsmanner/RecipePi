from recipepi.recipe.graph import Node


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