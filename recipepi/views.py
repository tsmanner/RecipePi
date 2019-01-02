from pyramid.view import view_config
from pyramid.response import Response
from recipepi.recipe import Recipe, NodeGroup, parse_recipe


AUTHORIZED_USERS = {
    'Tsmanner',
}


@view_config(route_name='recipe')
def recipe(request):
    for key in request.POST:
        print('    {}: {}'.format(key, request.POST.getall(key)))
    recipe_html = ''
    license_html = ''
    if 'body' in request.POST:
        recipe = parse_recipe(request.POST['body'])
        recipe_html += recipe.render_html()

    page_html = '''\
{table}

<footer>{license}</footer>
'''.format(table=recipe_html, license=license_html)
    response = request.response
    response.body = bytes(page_html, request.url_encoding)
    response.headers["Access-Control-Allow-Origin"] = "*"
    return response
