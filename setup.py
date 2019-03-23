from setuptools import setup

with open('README.rst') as f:
    readme = f.read()

setup(name='over_stats',
      version='0.4.0',
      description='Python API to retrieve Overwatch Statistics',
      long_description=readme,
      long_description_content_type='text/x-rst',
      url='https://github.com/CRamsan/over-stats',
      author='Cramsan',
      author_email='contact@cramsan.com',
      classifiers=[
            'Development Status :: 4 - Beta',
            'Environment :: Console',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
            'Operating System :: OS Independent',
            'Programming Language :: Python :: 3.6',
            'Topic :: Games/Entertainment',
            'Topic :: Software Development :: Libraries :: Python Modules'
          ],
      keywords='overwatch stats statistics ',
      license='GNU GPL3',
      python_requires='>=3.6',      
      packages=['over_stats'],
      install_requires=['requests-html'],
      zip_safe=False)
