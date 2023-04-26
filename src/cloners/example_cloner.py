"""Bare minimum example for a new cloner

In order to add a new cloner :
    1. Create a new class
    2. Set cls._ACTIVE attribute to True
    3. Set cls._NAME attribute to some string
    4. Add string used for cls._NAME to config['enabled_cloners']
    5. Add an import statement for the new class to the cloner manager module
    5. Now the cloner manager should find it
"""


class ExampleCloner:
    _ACTIVE = True
    _NAME = 'Example'
