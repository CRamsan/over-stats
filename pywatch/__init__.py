import urllib
import requests_html

import pywatch.errors

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
    def __init__(self, battletag=None, platform='pc'):
        if platform == 'pc':
            try:
                self._battletag = urllib.parse.quote(battletag.replace('#', '-'))
            except AttributeError:
                raise InvalidBattletag(f'battletag="{battletag}" is invalid')
        elif platform not in PLATFORMS:
                raise InvalidArgument(f'platform="{platform}" is invalid')
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
        if len(html) != 1:
            raise UnexpectedBehaviour('Finding the element for this game mode returned 0 or more than 1 element')
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
            raise UnexpectedBehaviour('Found multiple comparison stats for this value.')
        stat = comparison_list[0]
        # stat_data will be in the form of ['dva' , '3' , 'reaper' , '6' , ....] 
        # We want to convert this into a dictionary
        stat_data = stat.text.split('\n')
        stat_dict = {}
        it = iter(stat_data)
        for hero_name in it:
            stat_value = next(it)
            stat_dict[hero_name] = stat_value
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
            raise UnexpectedBehaviour('Found multiple heros for this value.')
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
                stat_dict[stat_name] = stat_value
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
            raise UnexpectedBehaviour('Found multiple achievement types for this value.')
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
    Search for a <select> that matches the selectId. If no pageSection is provided we are going to search the whole page.
    If we find more than one matching <select> an exception will be thrown. 
    This method will then search for each <option> and it will return a dictionary that uses their text as the key.
    '''
    @staticmethod
    def getDictFromDropdown(selectId, pageSection):
        dropdownList = pageSection.find(f'select[data-group-id="{selectId}"]')
        if len(dropdownList) != 1:
            raise UnexpectedBehaviour('Found multiple dropdowns found.')
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
    '''
    Return the content of _model. If _model is still empty then a load_data_if_needed() will ensure to make a request 
    to populate it.
    '''
    def raw_data(self):
        self.load_data_if_needed()
        return self._model

    '''
    If _model is not populated or if force is tue, we will try to populate _model. Otherwise this method will be a noop.
    '''
    def load_data(self, force = False):
        if force:
            seld._model = {}
        self.load_data_if_needed()

    def comparison_types(self, mode):
        return list(self.raw_data[mode][COMPARISON].keys())

    def comparison_heroes(self, mode, comparison_type):
        return list(self.raw_data[mode][COMPARISON][comparison_type].keys())
    
    def comparisons(self, mode, comparison_type = None, comparison_hero = None):
        if comparison_type == None:
            return self.raw_data[mode][COMPARISON]
        elif comparison_hero == None:
            return self.raw_data[mode][COMPARISON][comparison_type]
        else:
            return self.raw_data[mode][COMPARISON][comparison_type][comparison_hero]

    def stat_heroes(self, mode):
        return list(self.raw_data[mode][STATS].keys())
 
    def stat_categories(self, mode, hero):
        return list(self.raw_data[mode][STATS][hero].keys())
    
    def stat_names(self, mode, hero, category):
        return list(self.raw_data[mode][STATS][hero][category].keys())
 
    def stats(self, mode, hero = None, category = None, stat_name = None):
        if hero == None:
            return self.raw_data[mode][STATS]
        elif category == None:
            return self.raw_data[mode][STATS][hero]
        elif stat_name == None:
            return self.raw_data[mode][STATS][hero][category]
        else:
            return self.raw_data[mode][STATS][hero][category][stat_name]
    
    def achievement_types(self):
        return list(self.raw_data[ACHIEVEMENTS].keys())

    def achievement_names(self, achievement_type):
        return list(self.raw_data[ACHIEVEMENTS][achievement_type].keys())

    def achievements(self, achievement_type = None, achievement_name = None, list_name = None):
        if achievement_type == None:
            return self.raw_data[ACHIEVEMENTS]
        elif achievement_name == None:
            return self.raw_data[ACHIEVEMENTS][achievement_type]
        else:
            return self.raw_data[ACHIEVEMENTS][achievement_type][list_name]
