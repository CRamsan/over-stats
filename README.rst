Pywatch
=======================

Python API to retrieve Overwatch statistics
Still in early development but accepting suggestions and PRs.

Installation
------------

    pip install pywatch

Requirements
------------
Python 3.6


Usage
------------

Initialize a player profile by providing the player tag and the platform. The platform is optional and it defaults to 'pc'. Other valid values are 'xbl' and 'psn'

.. code:: python

        player_data = pywatch.PlayerProfile('Stylosa#21555')
or

.. code:: python

        player_data = pywatch.PlayerProfile('acesarramsan', pywatch.PLAT_PSN)

Download and parse the profile's data. You do not need to call this method because the first method that needs to download the profile data will do so. 

.. code:: python

        player_data.load_data()

Print the entire profile's data in JSON format.

.. code:: python

        import json
        print (json.dumps(player_data.raw_data, indent=4))

You can find a more methods to access the data in the demo.py file.
