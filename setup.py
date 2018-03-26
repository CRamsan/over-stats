from setuptools import setup

setup(name='over_stats',
      version='0.2',
      description='Python API to retrieve Overwatch Statistics',
      url='https://github.com/CRamsan/over-stats',
      author='Cramsan',
      author_email='contact@cramsan.com',
      license='GNU GPL3',
      python_requires='>=3.6',      
      packages=['over_stats'],
      install_requires=['requests-html'],
      zip_safe=False)
