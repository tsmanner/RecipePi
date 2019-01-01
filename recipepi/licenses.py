""" License Objects
"""


from collections import namedtuple


License = namedtuple('License', ('name', 'text', 'html'))


class License:
    def __init__(self, name, licensor, version, html):
        self.name = name
        self.licensor = licensor
        self.version = version
        self.html = html

    def render(self):
        pass


BY_NC_SA = License(
    name= 'Creative Commons BY_NC_SA',
    licensor = None,
    version = '4.0',
    html = '''\
<a rel="license" href="http://creativecommons.org/licenses/by-nc-sa/4.0/"><img alt="Creative Commons License" style="border-width:0" src="https://i.creativecommons.org/l/by-nc-sa/4.0/88x31.png" /></a><br />
This work is licensed under a <a rel="license" href="http://creativecommons.org/licenses/by-nc-sa/4.0/">Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License</a>.\
'''
)


