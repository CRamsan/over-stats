import json
import over_stats
import pytest
import time

'''
Test initializing the API with different kinds of profiles.
'''
def test_initialize():
    # Test the PC profile
    player_data = over_stats.PlayerProfile('zappis#21285')
    assert type(player_data.raw_data) is dict

    # Test a PC profile by setting the platform parameter
    player_data = over_stats.PlayerProfile('zappis#21285', over_stats.PLAT_PC)
    assert type(player_data.raw_data) is dict
    
    # Test a PC profile by setting the platform parameter and using Decimals to wrap floats
    player_data = over_stats.PlayerProfile('zappis#21285', over_stats.PLAT_PC, True)
    assert type(player_data.raw_data) is dict
    
    # Test a non existing PC profile
    with pytest.raises(over_stats.errors.PlayerNotFound):
        player_data = over_stats.PlayerProfile('zappis#21286', over_stats.PLAT_PC, True)
        player_data.raw_data

    # Test a PSN profile
    player_data = over_stats.PlayerProfile('EhhFreezy', over_stats.PLAT_PSN)
    assert type(player_data.raw_data) is dict
   
    # Test a non existing PSN profile
    with pytest.raises(over_stats.errors.PlayerNotFound):
        player_data = over_stats.PlayerProfile('ThisIsNotAnExistingProfile', over_stats.PLAT_PC, True)
        player_data.raw_data

    # Test an XBL profile
    player_data = over_stats.PlayerProfile('Dethroned', over_stats.PLAT_XBL)
    assert type(player_data.raw_data) is dict
   
    # Test a non existing XBL profile
    with pytest.raises(over_stats.errors.PlayerNotFound):
        player_data = over_stats.PlayerProfile('AnotherNonExistigProfile', over_stats.PLAT_PC, True)
        player_data.raw_data

'''
Test that the player data is not loaded when the object is created.
'''
def test_object_init_perf():
    start_time = time.perf_counter()
    player_data = over_stats.PlayerProfile('acesarramsan', over_stats.PLAT_PSN)
    end_time = time.perf_counter()
    result = end_time - start_time
    assert result < 0.0001

'''
Test that the player data is loaded when it is first needed
'''
def test_data_on_demand():
    player_data = over_stats.PlayerProfile('acesarramsan', over_stats.PLAT_PSN)
    start_time = time.perf_counter()
    player_data.raw_data
    end_time = time.perf_counter()
    result = end_time - start_time
    assert result < 4

'''
Test JSON serialization
'''
def test_json_dump():
    player_data = over_stats.PlayerProfile('acesarramsan', over_stats.PLAT_PSN)
    result = json.dumps(player_data.raw_data)
    assert type(result) is str

'''
Test JSON error when trying to dump a Decimal object
'''
def test_json_dump_decimal():
    player_data = over_stats.PlayerProfile('acesarramsan', over_stats.PLAT_PSN, True)
    with pytest.raises(TypeError):
        result = json.dumps(player_data.raw_data)

'''
Test that we are getting the expected types from the methods to iterate and retrieve values
'''
def test_data_structure():
    player_data = over_stats.PlayerProfile('acesarramsan', over_stats.PLAT_PSN)
    
    assert len(over_stats.MODES) is 2
    for mode in over_stats.MODES:
        assert type(player_data.comparison_types(mode)) is list
        for comparison_type in player_data.comparison_types(mode):
            assert type(player_data.comparison_heroes(mode, comparison_type )) is list
            for comparison_hero in player_data.comparison_heroes(mode, comparison_type):
                assert (player_data.comparisons(mode, comparison_type, comparison_hero)) is not None

        assert type(player_data.stat_heroes(mode)) is list
        for hero in player_data.stat_heroes(mode):
            assert type(player_data.stat_categories(mode, hero)) is list
            for category in player_data.stat_categories(mode, hero):
                assert type(player_data.stat_names(mode, hero, category)) is list
                for stat_name in player_data.stat_names(mode, hero, category):
                    assert (player_data.stats(mode, hero, category, stat_name)) is not None

    assert type(player_data.achievement_types()) is list
    for achievement_type in player_data.achievement_types():
        for achievement in player_data.achievements(achievement_type, over_stats.ACH_EARNED):
            assert type(achievement) is str
        for achievement in player_data.achievements(achievement_type, over_stats.ACH_MISSING):
            assert type(achievement) is str
