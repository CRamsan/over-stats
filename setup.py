from setuptools import setup

setup(name='pywatch',
      version='0.1',
      description='Python API to retrieve Overwatch statistics',
      url='https://github.com/CRamsan/pywatch',
      author='Cramsan',
      author_email='contact@cramsan.com',
      license='GNU GPL3',
      packages=['pywatch'],
      install_requires=['requests-html'],
      zip_safe=False)
