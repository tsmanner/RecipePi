""" Utility library to handle SVG creation
"""
import svgwrite


def svg(item, *args, **kwargs):
    return item.__svg__(*args, **kwargs)


class SvgProxy:
    def __init__(self, proxied, tagname):
        self.tagname = tagname
        self.attributes = {}
        self.contents = []

    def __svg__(self):
        s = "<" + self.tagname
        s += "".join([" " + str(k) + '="' + str(v) + '"' for k, v in self.attributes.items()])
        s += ">"
        s += "\n".join([svg(item) for item in self.contents])
        return s


class SvgRecipe:
    def __init__(self):
        self.ingredients = []

    def svg_digraph(self, indent="", **kwargs):
        tokens = [
            '<svg',
            ' xmlns="http://www.w3.org/2000/svg"',
            ' xmlns:ev="http://www.w3.org/2001/xml-events"',
            ' xmlns:xlink="http://www.w3.org/1999/xlink"',
            ''.join([' {}="{}"'.format(k, v) for k, v in kwargs.items()]),
            '>',
        ]
        for ingredient in self.ingredients:
            tokens.append('\n' + indent + ingredient.svg_digraph())
        tokens.append('\n</svg>')
        return ''.join(tokens)


class SvgIngredient:
    def svg_digraph(self, **kwargs):
        font_size = 16
        padding = 2
        width = 50
        height = font_size + padding + padding
        points = [
            width, 0,
            0, 0,
            0, height,
            width, height,
        ]
        tokens = [
            '<defs>'
            '<polyline',
            ' id=ingredient_cell',
            ' fill="none"',
            ' stroke="black"',
            ' points="{}"'.format(' '.join([str(point) for point in points])),
            '/>',
            '</defs>'
            '<text',
            ' style: "font-size={};'.format(font_size),
            ' shape-inside: url(#ingredient_cell);"',
            '>',
            '{} {}'.format(self.name, self.amount),
            '</text>',
        ]
        return ''.join(tokens)
