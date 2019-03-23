from decimal import *
import urllib.parse
import requests_html

import over_stats.errors

PLAT_PC = "pc"
PLAT_XBL = "xbl"
PLAT_PSN = "psn"
PLATFORMS = [PLAT_PC, PLAT_XBL, PLAT_PSN]
MODE_QP = "quickplay"
MODE_CP = "competitive"
MODE_LIST = [MODE_QP, MODE_CP]
COMPARISON = 'comparisons'
STATS = 'stats'
MODES = 'modes'
ACHIEVEMENTS = 'achievements'
ACH_EARNED = 'earned'
ACH_MISSING = 'missing'

session = requests_html.HTMLSession()


class PlayerProfile:
    def __init__(self, battletag=None, platform=PLAT_PC, use_decimal=False):
        """Create a new player profile."""

        if platform == PLAT_PC:
            try:
                self._battletag = urllib.parse.quote(battletag.replace('#', '-'))
            except AttributeError:
                raise over_stats.errors.InvalidBattletag(f'battletag="{battletag}" is invalid')
        elif platform not in PLATFORMS:
                raise over_stats.errors.InvalidArgument(f'platform="{platform}" is invalid')
        else:
            self._battletag = urllib.parse.quote(battletag)
        self._platform = platform
        self._model = None
        self._use_decimal = use_decimal
        self.url = 'https://playoverwatch.com/en-us/career/' + platform + '/' + self._battletag

    # Internal methods
    def get_html_for_mode(self, mode):
        """
        Used to retrieve the html element that contains all the data for competitive or quickplay.
        """
        html = self._r.html.find(f'div[id="{mode}"]')
        if len(html) == 0:
            raise over_stats.errors.PlayerNotFound(f'Mode "{mode}" was not found. There is no data for this player')
        if len(html) != 1:
            raise over_stats.errors.UnexpectedBehaviour('Finding the element for this game mode returned more than 1 element')

        return html[0]

    def load_data_if_needed(self):
        """
        This method will check if the _model variable holds any data, and if it does then return it. If it is empty
        then a network request will be made to download the player profile data and it will be parsed and stored in
        the _model variable.

        """
        if self._model is None:
            self._model = {
                    MODES: {},
                    ACHIEVEMENTS: {}
                    }
            self._r = session.get(self.url)
            # We are assuming that OW will not have any other game modes other than competitive and quickplay. 
            for mode in MODE_LIST:
                # now get the html content that belongs to the current game mode
                html_mode = None
                try:
                    html_mode = self.get_html_for_mode(mode)
                except over_stats.errors.PlayerNotFound:
                    # If the player has not played in a mode, then the html element will be missing. 
                    # We can safely skip it in this case.
                    continue

                mode_dict = {}

                # now retrieve the dictionary for all the different comparisons available, they will be something
                # like 'Games Won', 'Time Played', 'Weapon Accuracy', etc
                comparison_dict = {}
                comparisons = self.get_dict_from_dropdown(COMPARISON, html_mode)
                for comp_name, comp_value in comparisons.items():
                    comparison_stats = self.generate_comparison_stats(html_mode, comp_value, self._use_decimal)
                    comparison_dict[comp_name] = comparison_stats
                mode_dict[COMPARISON] = comparison_dict

                # Now we are going to parse the career stat section
                hero_stat_dict = {}
                # Generate the dictionary for the hero stats
                heroes = self.get_dict_from_dropdown(STATS, html_mode)
                # Now generate a dictionary using the hero name as the dictionary key
                for heroe_name, heroe_value in heroes.items():
                    hero_stats = self.generate_hero_stats(html_mode, heroe_value, self._use_decimal)
                    hero_stat_dict[heroe_name] = hero_stats
                mode_dict[STATS] = hero_stat_dict

                self._model[MODES][mode] = mode_dict

            achievements_dict = {}
            # Now extract the achievements
            achievements = self.get_dict_from_dropdown(ACHIEVEMENTS, self._r.html)
            # The achievement_type will be something like 'Offense', 'Defense', 'Tank', etc
            for achievement_type, achievement_type_value in achievements.items():
                achievement_dict = self.generate_achievement_list(self._r.html, achievement_type_value)
                achievements_dict[achievement_type] = achievement_dict
            self._model[ACHIEVEMENTS] = achievements_dict

    @staticmethod
    def generate_comparison_stats(html, comparison_value, use_decimal=False):
        """
        Search the html element for divs containing the comparison stats.
        The result will be a dictionary that uses a hero as it's key and the stat value as the value
        """
        comparison_list = html.find(f'div[data-category-id="{comparison_value}"]')
        if len(comparison_list) == 0:
            return []
        if len(comparison_list) != 1:
            raise over_stats.errors.UnexpectedBehaviour('Found multiple comparison stats for this value.')
        stat = comparison_list[0]
        # stat_data will be in the form of ['dva' , '3' , 'reaper' , '6' , ....] 
        # We want to convert this into a dictionary
        stat_data = stat.text.split('\n')
        stat_dict = {}
        it = iter(stat_data)
        for hero_name in it:
            stat_value = next(it)
            stat_dict[hero_name] = PlayerProfile.handle_stat_value(stat_value, use_decimal)
        return stat_dict

    @staticmethod
    def generate_hero_stats(html, hero_value, use_decimal=False):
        """
        Search the html element for all divs containing the hero stat card. Each card will contain a list of
        stats. The result will be a dictionary of stat categories names that link to a dictionary of stat names
        and values.
        """
        hero_category_list = html.find(f'div[data-category-id="{hero_value}"]')
        if len(hero_category_list) == 0:
            return []
        if len(hero_category_list) != 1:
            raise over_stats.errors.UnexpectedBehaviour('Found multiple heros for this value.')
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
                stat_dict[stat_name] = PlayerProfile.handle_stat_value(stat_value, use_decimal)
            card_dict[card_title] = stat_dict
        return card_dict

    @staticmethod
    def generate_achievement_list(html, achievement_type_value):
        """
        Search the html element for a div that matches the achievement_type_value. This div will contain a list of achievements.
        The return value will be a dictionary containing two lists, one for acquired and one for missing achievements. Each list
        will contain the names of the respective achievements.
        """
        achievement_type_list = html.find(f'div[data-category-id="{achievement_type_value}"]')
        if len(achievement_type_list) == 0:
            return []
        if len(achievement_type_list) != 1:
            raise over_stats.errors.UnexpectedBehaviour('Found multiple achievement types for this value.')
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

    @staticmethod
    def handle_stat_value(stat_value, use_decimal=False):
        """
        The values retrieved from the html is a string that represents different types of value types.
        This method will handle converting those strings into their appropriate value
        """
        if '--' == stat_value or ':' in stat_value:
            return stat_value
        elif '%' in stat_value:
            if use_decimal:
                return Decimal(str(float(stat_value.replace("%", "")) / 100.0))
            else:
                return float(stat_value.replace("%", "")) / 100.0
        elif ' ' in stat_value:
            return stat_value.split(" ")
        else:
            stat_value = stat_value.replace(',', '')
            if '.' in stat_value:
                return float(stat_value)
            else:
                return int(stat_value)

    @staticmethod
    def get_dict_from_dropdown(select_id, page_section):
        """
        Search for a <select> that matches the select_id. If no page_section is provided we are going to search the whole page.
        If we find more than one matching <select> an exception will be thrown.
        This method will then search for each <option> and it will return a dictionary that uses their text as the key.
        """
        dropdown_list = page_section.find(f'select[data-group-id="{select_id}"]')
        if len(dropdown_list) == 0:
            return {}
        if len(dropdown_list) > 1:
            raise over_stats.errors.UnexpectedBehaviour('Found multiple dropdowns found.')
        option_list = dropdown_list[0].find('option')
        option_dict = {}
        for option in option_list:
            text = option.text
            value = option.attrs['value']
            option_dict[text] = value
        return option_dict

    # Public APIs

    @property
    def raw_data(self):
        """
        Return the content of _model. If _model is still empty then a load_data_if_needed() will ensure to make a request 
        to populate it.
        """
        self.load_data_if_needed()
        return self._model

    def load_data(self, force=False):
        """
        If _model is not populated or if force is tue, we will try to populate _model. Otherwise this method will be a noop.
        """
        if force:
            self._model = {}
        self.load_data_if_needed()
    
    def modes(self):
        """
        Get a list of available game modes
        """
        return list(self.raw_data[MODES].keys())

    def comparison_types(self, mode):
        """
        Get a list of comparison types available for this game mode
        """
        return list(self.raw_data[MODES][mode][COMPARISON].keys())

    def comparison_heroes(self, mode, comparison_type):
        """
        Get a list of available heroes for this combination of comparison type and game mode
        """
        return list(self.raw_data[MODES][mode][COMPARISON][comparison_type].keys())

    def comparisons(self, mode, comparison_type=None, comparison_hero=None):
        """
        Get comparison data
        Retrieve the comparison data avilable for the provided game mode.
        You can specify comparison type, and comparison hero to narrow down the return values.
        """
        if mode not in MODE_LIST:
            raise over_stats.errors.InvalidArgument(f'mode="{mode}" is invalid')
        try:
            if comparison_type is None and comparison_hero is None:
                return self.raw_data[MODES][mode][COMPARISON]
            elif comparison_type is not None and comparison_hero is None:
                return self.raw_data[MODES][mode][COMPARISON][comparison_type]
            elif comparison_type is not None and comparison_hero is not None:
                return self.raw_data[MODES][mode][COMPARISON][comparison_type][comparison_hero]
            else:
                raise over_stats.errors.InvalidArgument(f'Combination of comparison_type="{comparison_type}", comparison_hero="{comparison_hero}" is not valid')
        except KeyError:
            raise over_stats.errors.DataNotFound("Data not available")

    def stat_heroes(self, mode):
        """
        Get a list of available heroes to get stats from for the provided game mode.
        """
        return list(self.raw_data[MODES][mode][STATS].keys())

    def stat_categories(self, mode, hero):
        """
        Get a list of available stat categories for the requested hero
        """
        return list(self.raw_data[MODES][mode][STATS][hero].keys())

    def stat_names(self, mode, hero, category):
        """
        Get a list of available stat names for the requested game mode, hero name and stat category
        """
        return list(self.raw_data[MODES][mode][STATS][hero][category].keys())

    def stats(self, mode, hero=None, category=None, stat_name=None):
        """
        Get stats data
        Retrieve the statistics data available for the provided game mode.
        You can provide a hero, category and stat name to narrow down the return value.
        """
        if mode not in MODE_LIST:
            raise over_stats.errors.InvalidArgument(f'mode="{mode}" is invalid')
        try:
            if hero is None and category is None and stat_name is None:
                return self.raw_data[MODES][mode][STATS]
            elif hero is not None and category is None and stat_name is None:
                return self.raw_data[MODES][mode][STATS][hero]
            elif hero is not None and category is not None and stat_name is None:
                return self.raw_data[MODES][mode][STATS][hero][category]
            elif hero is not None and category is not None and stat_name is not None:
                return self.raw_data[MODES][mode][STATS][hero][category][stat_name]
            else:
                raise over_stats.errors.InvalidArgument(f'Combination of hero="{hero}", category="{category}" and stat_name="{stat_name}" is not valid')
        except KeyError:
            raise over_stats.errors.DataNotFound("Data not available")

    def achievement_types(self):
        """
        Get a list of available achievement types.
        """
        return list(self.raw_data[ACHIEVEMENTS].keys())

    def achievements(self, achievement_type=None, list_name=None):
        """
        Get achievement data
        Retrieve the available achievement data for this player. You can specify an achievement type or a list name to
        narrow down the returned value. The list_name parameter can be None, over_stats.ACH_EARNED or over_stats.ACH_MISSING.
        """
        try:
            if achievement_type is None:
                return self.raw_data[ACHIEVEMENTS]
            elif list_name is None:
                return self.raw_data[ACHIEVEMENTS][achievement_type]
            else:
                return self.raw_data[ACHIEVEMENTS][achievement_type][list_name]
        except KeyError:
            raise over_stats.errors.DataNotFound("Data not available")
