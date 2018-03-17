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

Print the entire profile's data in JSON format. You will notice that the output is organized in a similar fashion as in the source (https://playoverwatch.com/).

.. code:: python

        import json
        print (json.dumps(player_data.raw_data, indent=4))

This library does not hardcode the list of heroes, statistics or achievements. Instead you will need to retrieve those available values for the specific type of data you are retrieving. Even though this approach makes this library a bit more complicated to use, it also allows that new values such as new heroes will be handled transparently. 

You can find more methods to access player data in the demo.py file.
