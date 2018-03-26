import urllib
import requests_html

import over-stats.errors

PLAT_PC = "pc"
PLAT_XBL = "xbl"
PLAT_PSN = "psn"
PLATFORMS = [PLAT_PC, PLAT_XBL, PLAT_PSN]
MODE_QP = "quickplay"
MODE_CP = "competitive"
MODES = [MODE_QP, MODE_CP]
COMPARISON = 'comparisons'
STATS = 'stats'
ACHIEVEMENTS = 'achievements'
ACH_EARNED = 'earned'
ACH_MISSING = 'missing'

session = requests_html.HTMLSession()

class PlayerProfile:

    '''
    Constructor
    '''
    def __init__(self, battletag=None, platform=PLAT_PC):
        if platform == PLAT_PC:
            try:
                self._battletag = urllib.parse.quote(battletag.replace('#', '-'))
            except AttributeError:
                raise over-stats.errors.InvalidBattletag(f'battletag="{battletag}" is invalid')
        elif platform not in PLATFORMS:
                raise over-stats.errors.InvalidArgument(f'platform="{platform}" is invalid')
        else:
            self._battletag = urllib.parse.quote(battletag)
        self._platform = platform
        self._model = None
        self.url = 'https://playoverwatch.com/en-us/career/' + platform + '/' + self._battletag

    '''
    Internal methods
    '''
        
    def get_html_for_mode(self, mode):
        '''
        Used to retrieve the html element that contains all the data for competitive or quickplay.
        '''
        html = self._r.html.find(f'div[id="{mode}"]')
        if len(html) == 0:
            raise over-stats.errors.PlayerNotFound(f'Mode "{mode}" was not found. There is no data for this player')
        if len(html) != 1:
            raise over-stats.errors.UnexpectedBehaviour('Finding the element for this game mode returned more than 1 element')
        
        return html[0]

    def load_data_if_needed(self):
        '''
        This method will check if the _model variable holds any data, and if it does then return it. If it is empty
        then a network request will be made to download the player profile data and it will be parsed and stored in
        the _model variable.

        '''
        if self._model == None:
            self._model = {}
            self._r = session.get(self.url)
            # We are assuming that OW will not have any other game modes other than competitive and quickplay. 
            for mode in MODES:
                # now get the html content that belongs to the current game mode
                html_mode = self.get_html_for_mode(mode)
                mode_dict = {}
                
                # now retrieve the dictionary for all the different comparisons available, they will be something
                # like 'Games Won', 'Time Played', 'Weapon Accuracy', etc
                comparison_dict = {}
                comparisons = self.getDictFromDropdown(COMPARISON, html_mode)
                for comp_name, comp_value in comparisons.items():
                    comparison_stats = self.generate_comparison_stats(html_mode, comp_value)
                    comparison_dict[comp_name] = comparison_stats
                mode_dict[COMPARISON] = comparison_dict
                
                # Now we are going to parse the career stat section
                hero_stat_dict = {}
                # Generate the dictionary for the hero stats
                heroes = self.getDictFromDropdown(STATS, html_mode)
                # Now generate a dictionary using the hero name as the dictionary key
                for heroe_name, heroe_value in heroes.items():
                    hero_stats = self.generate_hero_stats(html_mode, heroe_value)
                    hero_stat_dict[heroe_name] = hero_stats
                mode_dict[STATS] = hero_stat_dict
                
                self._model[mode] = mode_dict
            achievements_dict = {}
            # Now extract the achievements
            achievements = self.getDictFromDropdown(ACHIEVEMENTS, self._r.html)
            # The achievement_type will be something like 'Offense', 'Defense', 'Tank', etc
            for achievement_type, achievement_type_value in achievements.items():
                achievement_dict = self.generate_achievement_list(self._r.html, achievement_type_value)
                achievements_dict[achievement_type] = achievement_dict
            self._model[ACHIEVEMENTS] = achievements_dict
    
    '''
    Search the html element for divs containing the comparison stats.
    The result will be a dictionary that uses a hero as it's key and the stat value as the value
    '''
    @staticmethod
    def generate_comparison_stats(html, comparison_value):
        comparison_list = html.find(f'div[data-category-id="{comparison_value}"]')
        if len(comparison_list) == 0:
            return []
        if len(comparison_list) != 1:
            raise over-stats.errors.UnexpectedBehaviour('Found multiple comparison stats for this value.')
        stat = comparison_list[0]
        # stat_data will be in the form of ['dva' , '3' , 'reaper' , '6' , ....] 
        # We want to convert this into a dictionary
        stat_data = stat.text.split('\n')
        stat_dict = {}
        it = iter(stat_data)
        for hero_name in it:
            stat_value = next(it)
            stat_dict[hero_name] = PlayerProfile.handle_stat_value(stat_value)
        return stat_dict

    '''
    Search the html element for all divs containing the hero stat card. Each card will contain a list of
    stats. The result will be a dictionary of stat categories names that link to a dictionary of stat names
    and values.
    '''
    @staticmethod
    def generate_hero_stats(html, hero_value):
        hero_category_list = html.find(f'div[data-category-id="{hero_value}"]')
        if len(hero_category_list ) == 0:
            return []
        if len(hero_category_list ) != 1:
            raise over-stats.errors.UnexpectedBehaviour('Found multiple heros for this value.')
        hero_stats = hero_category_list[0]
        cards = hero_stats.find('.card-stat-block')
        # Each card represents the tables for 'Combat', 'Best', 'Average' etc
        card_dict = {}
        for card in cards:
            card_values = card.text.split("\n")
            card_title = card_values[0]
            # Each card will have a list of stats inside. Now iterate two at a time
            # to convert the stats into a dictionary
            card_content = card_values[1:]
            stat_dict = {}
            it = iter(card_content)
            for stat_name in it:
                stat_value = next(it)
                stat_dict[stat_name] = PlayerProfile.handle_stat_value(stat_value)
            card_dict[card_title] = stat_dict
        return card_dict

    '''
    Search the html element for a div that matches the achievement_type_value. This div will contain a list of achievements.
    The return value will be a dictionary containing two lists, one for acquired and one for missing achievements. Each list
    will contain the names of the respective achievements.
    '''
    @staticmethod
    def generate_achievement_list(html, achievement_type_value):
        achievement_type_list = html.find(f'div[data-category-id="{achievement_type_value}"]')
        if len(achievement_type_list) == 0:
            return []
        if len(achievement_type_list) != 1:
            raise over-stats.errors.UnexpectedBehaviour('Found multiple achievement types for this value.')
        achievement_container = achievement_type_list[0]
        achievement_list = achievement_container.find('.achievement-card')
        stat_dict = {}
        earned_achievement = []
        missing_achievement = []
        for achievement in achievement_list:
            achievement_name = achievement.text
            if len(achievement.find('.m-disabled')) == 0:
                earned_achievement.append(achievement_name)
            else:
                missing_achievement.append(achievement_name)
        stat_dict[ACH_EARNED] = earned_achievement
        stat_dict[ACH_MISSING] = missing_achievement
        return stat_dict

    '''
    The values retrieved from the html is a string that represents different types of value types.
    This method will handle converting those strings into their appropriate value
    '''
    @staticmethod
    def handle_stat_value(stat_value):
        if '--' == stat_value or ':' in stat_value:
            return stat_value
        elif '%' in stat_value:
            return float(stat_value.replace("%", ""))/(100.0)
        elif ' ' in stat_value:
            return stat_value.split(" ")
        else:
            stat_value = stat_value.replace(',', '')
            if '.' in stat_value:
                return float(stat_value)
            else:
                return int(stat_value)


    '''
    Search for a <select> that matches the selectId. If no pageSection is provided we are going to search the whole page.
    If we find more than one matching <select> an exception will be thrown. 
    This method will then search for each <option> and it will return a dictionary that uses their text as the key.
    '''
    @staticmethod
    def getDictFromDropdown(selectId, pageSection):
        dropdownList = pageSection.find(f'select[data-group-id="{selectId}"]')
        if len(dropdownList) != 1:
            raise over-stats.erros.UnexpectedBehaviour('Found multiple dropdowns found.')
        optionList = dropdownList[0].find('option')
        optionDict = {}
        for option in optionList:
            text = option.text
            value = option.attrs['value']
            optionDict[text] = value
        return optionDict

    '''
    Public APIs
    '''

    @property
    def raw_data(self):
        '''
        Return the content of _model. If _model is still empty then a load_data_if_needed() will ensure to make a request 
        to populate it.
        '''
        self.load_data_if_needed()
        return self._model

    '''
    If _model is not populated or if force is tue, we will try to populate _model. Otherwise this method will be a noop.
    '''
    def load_data(self, force = False):
        if force:
            seld._model = {}
        self.load_data_if_needed()

    '''
    Get a list of comparison types available for this game mode
    '''
    def comparison_types(self, mode):
        return list(self.raw_data[mode][COMPARISON].keys())

    '''
    Get a list of available heroes for this combination of comparison type and game mode
    '''
    def comparison_heroes(self, mode, comparison_type):
        return list(self.raw_data[mode][COMPARISON][comparison_type].keys())
   
    '''
    Get comparison data
    Retrieve the comparison data avilable for the provided game mode.
    You can specify comparison type, and comparison hero to narrow down the return values.
    '''
    def comparisons(self, mode, comparison_type = None, comparison_hero = None):
        if mode not in MODES:
            raise over-stats.errors.InvalidArgument(f'mode="{mode}" is invalid')
        try:
            if comparison_type == None and comparison_hero == None:
                return self.raw_data[mode][COMPARISON]
            elif comparison_type != None and comparison_hero == None:
                return self.raw_data[mode][COMPARISON][comparison_type]
            elif comparison_type != None and comparison_hero != None:
                return self.raw_data[mode][COMPARISON][comparison_type][comparison_hero]
            else:
                raise over-stats.errors.InvalidArgument(f'Combination of comparison_type="{comparison_type}", comparison_hero="{comparison_hero}" is not valid')
        except KeyError:
            raise over-stats.errors.DataNotFound("Data not available")

    '''
    Get a list of available heroes to get stats from for the provided game mode.
    '''
    def stat_heroes(self, mode):
        return list(self.raw_data[mode][STATS].keys())
 
    '''
    Get a list of available stat categories for the requested hero
    '''
    def stat_categories(self, mode, hero):
        return list(self.raw_data[mode][STATS][hero].keys())
    
    '''
    Get a list of available stat names for the requested game mode, hero name and stat category
    '''
    def stat_names(self, mode, hero, category):
        return list(self.raw_data[mode][STATS][hero][category].keys())

    '''
    Get stats data
    Retrieve the statistics data available for the provided game mode.
    You can provide a hero, category and stat name to narrow down the return value.
    '''
    def stats(self, mode, hero = None, category = None, stat_name = None):
        if mode not in MODES:
            raise over-stats.errors.InvalidArgument(f'mode="{mode}" is invalid')
        try:
            if hero == None and category == None and stat_name == None:
                return self.raw_data[mode][STATS]
            elif hero != None and category == None and stat_name == None:
                return self.raw_data[mode][STATS][hero]
            elif hero != None and category != None and stat_name == None:
                return self.raw_data[mode][STATS][hero][category]
            elif hero != None and category != None and stat_name != None:
                return self.raw_data[mode][STATS][hero][category][stat_name]
            else:
                raise over-stats.errors.InvalidArgument(f'Combination of hero="{hero}", category="{category}" and stat_name="{stat_name}" is not valid')
        except KeyError:
            raise over-stats.errors.DataNotFound("Data not available")

    '''
    Get a list of available achievement types.
    '''
    def achievement_types(self):
        return list(self.raw_data[ACHIEVEMENTS].keys())

    '''
    Get achievement data
    Retrieve the available achievement data for this player. You can specify an achievement type or a list name to
    narrow down the returned value. The list_name parameter can be None, over-stats.ACH_EARNED or over-stats.ACH_MISSING. 
    '''
    def achievements(self, achievement_type = None, list_name = None):
        try:
            if achievement_type == None:
                return self.raw_data[ACHIEVEMENTS]
            elif list_name == None:
                return self.raw_data[ACHIEVEMENTS][achievement_type]
            else:
                return self.raw_data[ACHIEVEMENTS][achievement_type][list_name]
        except KeyError:
            raise over-stats.errors.DataNotFound("Data not available")


