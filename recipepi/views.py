from pyramid.view import view_config
from recipepi.renderers.html import render_html
from recipepi.recipe.recipe import Recipe
from recipepi.parsers.parser import parse_recipe


AUTHORIZED_USERS = {
    'Tsmanner',
}


@view_config(route_name='recipe')
def get_recipe(request):
    for key in request.POST:
        print('    {}: {}'.format(key, request.POST.getall(key)))
    recipe_html = ''
    license_html = ''
    if 'body' in request.POST:
        recipe = parse_recipe(request.POST['body'])
        if isinstance(recipe, Recipe):
            recipe_html += render_html(recipe)
        else:
            recipe_html = '<span style="color: red;"><b>{}</b></span>'.format(recipe)

    page_html = '''\
{table}

<footer>{license}</footer>
'''.format(table=recipe_html, license=license_html)
    response = request.response
    response.body = bytes(page_html, request.url_encoding)
    response.headers["Access-Control-Allow-Origin"] = "*"
    return response
