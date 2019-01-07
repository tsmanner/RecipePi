import time
from recipepi.parsers.parser import parse_recipe
from recipepi.recipe.recipe import Recipe
from recipepi.renderers.html import HTMLDataCell, HTMLTable, render_html

table = HTMLTable()
table.attributes["style"] = "border-spacing: 0;"

table[0][0] = HTMLDataCell("foo")
# table[0][1] = HTMLCell("bar")
bar = HTMLDataCell("bar")
table[2][1] = HTMLDataCell("baz")


bar.rowspan = 2
bar.colspan = 2
# table[0][1].rowspan = 2
# table[0][1].colspan = 2

table[0][1] = bar

print(table.dump())
print()
# table.render()
# print(table.dump())
# print()

for cell in table.values():
    cell.attributes["height"] = 25
    cell.attributes["width"] = 50
    cell.border["top"] = True
    cell.border["bottom"] = True
    # cell.border["left"] = True
    cell.border["right"] = True

table[1][0].border["right"] = False

table.collapse_borders()

recipe = parse_recipe('')
with open('rawr.html', 'w') as htmlfile:
    htmlfile.write(table.render())
    if isinstance(recipe, Recipe):
        htmlfile.write(render_html(recipe))

time.sleep(1)

table1 = HTMLTable()
table1[1][1] = HTMLDataCell("rawr")

print()
print(table1.dump())
print()
print(table.dump())
combined = table.insert_table(table.Coordinate(0, 0), table1, 'right')

print(combined.dump())
print()
print("table   ", id(table))
print("table1  ", id(table1))
print("combined", id(combined))
