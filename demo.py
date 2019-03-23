import json
import over_stats

# Initialize a player profile by providing the player tag and the platform.
# the platform is optional and by default it is 'pc'. Other valid values are
# 'xbl' and 'psn'
player_data = over_stats.PlayerProfile('ZanyDruid#13868')
# or
# player_data = over_stats.PlayerProfile('acesarramsan', over_stats.PLAT_PSN)

# Ther is a bug in the boto3 library that causes it not to be able to handle
# floats. To get around this issue there is flag that you can use to wrap floats
# into a Decimal. Be careful that Decimals cannot be dumped to json.
# player_data = over_stats.PlayerProfile('acesarramsan', over_stats.PLAT_PSN, True)

# Download and parse the profile's data
player_data.load_data()

# Print the entire profile's data in JSON format
# print (json.dumps(player_data.raw_data, indent=4))

# You can also use the helper methods to access the data you want
for mode in player_data.modes():
    # mode will be 'quickplay' or 'competitive'
    print (f"Game Mode: {mode}")
    print ("Comparison Types Available: " + str(player_data.comparison_types(mode)))
    for comparison_type in player_data.comparison_types(mode):
        # A comparison type will be one of the options in the 'Top Heroes' section, 'Times Played', 'Games Won',
        # 'Weapon Accuracy', etc
        print (f" - Comparison Type: {comparison_type}")
        print (" - Heroes available to compare: " + str(player_data.comparison_heroes(mode, comparison_type)))
        for comparison_hero in player_data.comparison_heroes(mode, comparison_type):
            # The comparison_hero be each hero in this list. The comparisons() method will return the value linked to each hero
            print ("    - " + comparison_hero + ": " + str(player_data.comparisons(mode, comparison_type, comparison_hero)))

    # This data belongs to the 'career_stats'. The values for hero will be 'All Heroes', 'Reaper', 'Tracer', etc.
    print ("Heroes with Stats Available: " + str(player_data.stat_heroes(mode)))
    for hero in player_data.stat_heroes(mode):
        print (f" - Hero: {hero}")
        # The category represents each card in for the selected hero, for example 'Combat', 'Assists', etc.
        print (" - Categories available for stats " + str(player_data.stat_categories(mode, hero)))
        for category in player_data.stat_categories(mode, hero):
            print (f"    - Category: {category}")
            print ("    - Stats available: " + str(player_data.stat_names(mode, hero, category)))
            for stat_name in player_data.stat_names(mode, hero, category):
                # This will print each stat from each category along with it's value
                print ("       - " + stat_name + ": " + str(player_data.stats(mode, hero, category, stat_name)))

# Achievements do not depend on game mode and instead they use categories like 'General', 'Offence', 'Defense', etc
print ("Achievement Types Available: " + str(player_data.achievement_types()))
for achievement_type in player_data.achievement_types():
    print (f"Achievement Type: {achievement_type}")
    # Each achievement category contains two lists, one with acquired achievements and one for missing achievements.
    print (f" - {over_stats.ACH_EARNED}")
    for achievement in player_data.achievements(achievement_type, over_stats.ACH_EARNED):
        # Print each earned achievements
        print (f"    - {achievement}")
    print (f" - {over_stats.ACH_MISSING}")
    for achievement in player_data.achievements(achievement_type, over_stats.ACH_MISSING):
        # Print each achievement that this player does not yet have
        print (f"    - {achievement}")
