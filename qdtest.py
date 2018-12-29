from recipepi.recipe import Recipe, NodeGroup, render_recipe_html


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

render_recipe_html(r)
