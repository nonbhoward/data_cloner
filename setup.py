# Solution to parent/sibling import conflicts without sys.path modification

# imports, python
from setuptools import find_packages
from setuptools import setup

setup(name='data_cloner', version='1.0', packages=find_packages())
