import json
import pywatch

player_data = pywatch.PlayerProfile('Stylosa#21555')
#player_data = pywatch.PlayerProfile('acesarramsan', pywatch.PLAT_PSN)

player_data.load_data()


# Initialize a player profile by providing the player tag and the platform.
# the platform is optional and by default it is 'pc'. Other valid values are
# 'xbl' and 'psn'
player_data = pywatch.PlayerProfile('Stylosa#21555')
# or
player_data = pywatch.PlayerProfile('acesarramsan', pywatch.PLAT_PSN)

# Download and parse the profile's data
player_data.load_data()

# Print the entire profile's data in JSON format
print (json.dumps(player_data.raw_data, indent=4))

# You can also use the helper methods to access the data you want
for mode in pywatch.MODES:
    # mode will be 'quickplay' or 'competitive'
    print (f"Game Mode: {mode}")
    for comparison_type in player_data.comparison_types(mode):
        # A comparison type will be one of the options in the 'Top Heroes' section, 'Times Played', 'Games Won',
        # 'Weapon Accuracy', etc
        print (f" - Comparison Type: {comparison_type}")
        for comparison_hero in player_data.comparison_heroes(mode, comparison_type):
            # The comparison_hero be each hero in this list. The comparisons() method will return the value linked to each hero
            print ("    - " + comparison_hero + ": " + player_data.comparisons(mode, comparison_type, comparison_hero))

    # This data belongs to the 'career_stats'. The values for hero will be 'All Heroes', 'Reaper', 'Tracer', etc.
    for hero in player_data.stat_heroes(mode):
        print (f" - Hero: {hero}")
        # The category represents each card in for the selected hero, for example 'Combat', 'Assists', etc.
        for category in player_data.stat_categories(mode, hero):
            print (f"    - Category: {category}")
            for stat_name in player_data.stat_names(mode, hero, category):
                # This will print each stat from each category along with it's value
                print ("       - " + stat_name + ": " + player_data.stats(mode, hero, category, stat_name))

# Achievements do not depend on game mode and instead they use categories like 'General', 'Offence', 'Defense', etc
for achievement_type in player_data.achievement_types():
    print (f"Achievement Type: {achievement_type}")
    for achievement_name in player_data.achievement_names(achievement_type):
        # Each achievement category contains two lists, one with acquired achievements and one for missing achievements.
        print (f" - {pywatch.ACH_EARNED}")
        for achievement in player_data.achievements(achievement_type, achievement_name, pywatch.ACH_EARNED):
            # Print each earned achievements
            print (f"    - {achievement}")
        print (f" - {pywatch.ACH_MISSING}")
        for achievement in player_data.achievements(achievement_type, achievement_name, pywatch.ACH_MISSING):
            # Print each achievement that this player does not yet have
            print (f"    - {achievement}")
