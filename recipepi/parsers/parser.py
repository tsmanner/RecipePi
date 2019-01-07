import textx

from recipepi.recipe.graph import NodeGroup
from recipepi.recipe.recipe import Recipe


grammar = '''
Model: ingredients*=Ingredient;
Ingredient:
    'ingredient' index=INT name_tokens=IngredientNameToken+
    amount=Amount
    ;

IngredientNameToken:
    !Amount /\w+/
    ;

Amount: 'amount:' value=/\w+([ \t\r\f\v]+\w+)*/;
'''

metamodel = textx.metamodel_from_str(grammar)

print("Grammar loaded successfully!")


def textx_parse(recipe_text):
    """
    Textx parse and return a model object or string if there's an error
    :param recipe_text: The string to parse
    :return: textx.
    """
    try:
        model = metamodel.model_from_str(recipe_text)
        if not hasattr(model, "ingredients"):
            model.ingredients = []
        return model
    except textx.exceptions.TextXSyntaxError as err:
        return '{}: {}'.format(err.__class__.__name__, err.message)
    except AttributeError as err:
        return '{}: {}'.format(err.__class__.__name__, str(err))


def parse_recipe(recipe_text):
    """ Parse the recipe text, returning a Recipe object
    """
    print("Parsing:")
    print(recipe_text)
    model = textx_parse(recipe_text)

    r = Recipe("Tom's Chili")
    ingredients = {}

    if not isinstance(model, str):
        for ingredient in model.ingredients:
            name = ' '.join(ingredient.name_tokens)
            print("{}: {} of {}".format(
                ingredient.index, ingredient.amount.value, ' '.join(ingredient.name_tokens)))
            ingredients[ingredient.index] = r.ingredient(name, ingredient.amount.value)

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
