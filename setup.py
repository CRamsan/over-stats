from setuptools import setup

setup(name='over-stats',
      version='0.1',
      description='Python API to retrieve Overwatch Statistics',
      url='https://github.com/CRamsan/over-stats',
      author='Cramsan',
      author_email='contact@cramsan.com',
      license='GNU GPL3',
      python_requires='>=3.6',      
      packages=['over-stats'],
      install_requires=['requests-html'],
      zip_safe=False)
