over_stats
=======================

Python API to retrieve Overwatch statistics
Still in early development but accepting suggestions and PRs.

Installation
------------

    pip install over_stats

Requirements
------------
Python 3.6


Usage
------------

Initialize a player profile by providing the player tag and the platform. The platform is optional and it defaults to 'pc'. Other valid values are 'xbl' and 'psn'

.. code:: python

        player_data = over_stats.PlayerProfile('Stylosa#21555')
or

.. code:: python

        player_data = over_stats.PlayerProfile('acesarramsan', over_stats.PLAT_PSN)

Download and parse the profile's data. You do not need to call this method because the first method that needs to download the profile data will do so. 

.. code:: python

        player_data.load_data()

Print the entire profile's data in JSON format. You will notice that the output is organized in a similar fashion as in the source (https://playoverwatch.com/).

.. code:: python

        import json
        print (json.dumps(player_data.raw_data, indent=4))

This library does not hardcode the list of heroes, statistics or achievements. Instead you will need to retrieve those available values for the specific type of data you are retrieving. Even though this approach makes this library a bit more complicated to use, it also allows that new values such as new heroes will be handled transparently. 

The list of game modes is available in:

.. code:: python

        over_stats.MODES

The fist section on a player's profile is the comparison section. Using one of the available modes you can retrieve the list of comparison types:

.. code:: python

        player_data.comparison_types(mode)

With a mode and a comparison type you can get the list of available heroes:

.. code:: python

        player_data.comparison_heroes(mode, comparison_type)

Providing a mode, comparison_type and comparison_hero you can get the exact stat value:

.. code:: python

        player_data.comparisons(mode, comparison_type, comparison_hero)

The mode parameter is required but comparison_type and comparison_hero are optionals. If you want to get the comparison data without been too specific you can provide a mode or a mode and a comparison_type.

The second section is the stat section. The list of heroes can be retrieved by providing a mode:

.. code:: python

        player_data.stat_heroes(mode)

With a hero and a mode you can retrieve the list of available stat categories:

.. code:: python

        player_data.stat_categories(mode, hero)

With a mode, hero and category you will be able to retrieve the list of available stats:

.. code:: python

        player_data.stat_names(mode, hero, category)

To retrieve the exact stat value you will need to provide a mode, hero, category and stat_name:

.. code:: python

        player_data.stats(mode, hero, category, stat_name)

The mode parameter is required but hero, category and stat_name are optional. You can also provide only a mode, a mode and a hero or a mode, a hero and a category.

The player's achievements are not divided between competitive and quickplay. In order to get a list of achievement types availeable you can do the following:

.. code:: python

        player_data.achievement_types()

With a achievement type and a list name, you can get a list of achievements.

.. code:: python

        player_data.achievements(achievement_type, over_stats.ACH_EARNED)
        player_data.achievements(achievement_type, over_stats.ACH_MISSING)

The achievement_type and list_name are optional arguments. You can also skip both or provide only an achievement_type.

You can find examples of how to use these methods in the demo.py file.
