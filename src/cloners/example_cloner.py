# Example cloner with minimal required properties

"""Bare minimum example for a new cloner

In order to add a new cloner :

    1. Create a new cloner class
    2. Set cls._ACTIVE attribute to True
    3. Set cls._NAME attribute to some string
    4. Add string used for cls._NAME to config attribute 'enabled_cloners'

Now the cloner manager should find it
"""


class ExampleCloner:
    _ACTIVE = True
    _NAME = 'Example'

    def authenticate(self):
        """
        This will authenticate with whatever API and be different for each
          cloner.
        """
        pass
