# -*- coding: utf-8 -*-
"""
Created on Mon Aug 17 17:57:24 2020

Author: Jordan Tanudjaja

Unit-testing Module for ygfandom.py
To be called with python -m pytest in the command line because pytest does not work since I did not
create this in development mode in a virtual environment
"""

from yugioh import ygfandom as ygf
import pandas as pd
import pytest


@pytest.fixture(scope = 'module') # Scope = 'module' is used to make sure this only runs once, and not after every test
def duelist():
    duelist = ygf.DbHandler(database_filepath = '../../Data/Yugioh Card Database.csv') # For testing purposes, the filepath is slightly routed for the test to access the database
    duelist.database_filepath = '../../Data/Yugioh Card Database (Testing).csv' # For testing purposes, the filepath to save the database in a test is changed to a separate file
    return duelist

@pytest.fixture
def scraper():
    scraper = ygf.YgScraper()
    yield scraper # teardown functionality needed here so that after every webtest, the sraper object is re-initalized before the next test,
                  # otherwise the previous card details and urls are carried over to next test

@pytest.mark.dbtest
class TestDbHandler:
    """
    Test Class to handle the unittesting of the DbHandler class in the ygfandom module
    """
    # Class-level variable to test the Yugioh Card Database following a certain format
    yugioh_columns = ('Card Name', 'Card Type', 'Spell/Trap Property', 'Attribute', 'Types',
                      'Level/Rank', 'ATK', 'DEF', 'LINK', 'Pendulum Scale',
                      'Card Description', 'Card/Attribute/Type Support',
                      'Direct Archetype & Series Support',
                      'Indirect Archetype & Series Support',
                      'Competitive Status (TCG Advanced)', 'Reference')

    def test_get_card_database(self, duelist):
        df = duelist.get_card_database()
        assert tuple(df.columns) == TestDbHandler.yugioh_columns # Columns in df should contain all the columns in yugioh_columns
        assert len(df) >= 10391 # Number of cards in the database should be at least 10391 (the number of cards that was first
                                # initialized there)


    def test_set_card_database(self, duelist):
        with pytest.raises(Exception) as error: # Not sure why InvalidDataFrameError cannot work here
            duelist.set_card_database(pd.DataFrame())
            duelist.set_card_database(pd.DataFrame(columns = TestDbHandler.yugioh_columns))
        assert str(error.value) == 'DataFrame is invalid and cannot be set as the Yugioh Card Database'


    def test_save_card_database(self, duelist):
        df = duelist.get_card_database()
        duelist.save_card_database() # Saving to the test database filepath
        df2 = pd.read_csv('../../Data/Yugioh Card Database (Testing).csv', keep_default_na = False)
        assert all(df == df2)


    def test_search_card_name(self, duelist):
        df = duelist.get_card_database()
        assert all(duelist.search_card_name('random name') == pd.DataFrame(columns = TestDbHandler.yugioh_columns))
        assert duelist.search_card_name('Cyber Dragon').index[0] == 4466
        assert duelist.search_card_name('cyber dragon').index[0] == 4466
        assert set(duelist.search_card_name(['cybEr DrAgoN', 'sdgsdg', 'dARk simOrGH', 'Cyber DRAgon']).index) == {4466, 7448}
        assert all(df == duelist.get_card_database()) # Making sure that the Original Database is not changed
                                                      # after invoking the seach_card_name method


    def test_locate_card(self, duelist):
        assert duelist.locate_card('https://www.google.com/') == None
        assert duelist.locate_card('https://yugioh.fandom.com/wiki/Swords_of_Revealing_Light') == 6051
        assert duelist.locate_card('https://yugioh.fandom.com/wiki/Imperial_Order') == 5066


    def test_add_card(self, duelist):
        with pytest.raises(Exception) as error:
            duelist.add_card('something')
            duelist.add_card({'random': 3, 'not yugi card': 4})
        assert str(error.value) == 'The card format passed is not correct, make sure you call YgSraper.get_card_details on the URL first'

        cyber_dragon = {'Card Name': 'Cyber Dragon',
                        'Card Type': 'Monster',
                        'Spell/Trap Property': 'N/A',
                        'Attribute': 'LIGHT',
                        'Types': 'Machine / Effect',
                        'Level/Rank': '5',
                        'ATK': '2100',
                        'DEF': '1600',
                        'LINK': 'N/A',
                        'Pendulum Scale': 'N/A',
                        'Card Description': 'If only your opponent controls a monster, you can Special Summon this card (from your hand).',
                        'Card/Attribute/Type Support': set(),
                        'Direct Archetype & Series Support': {'Cyber', 'Cyber Dragon'},
                        'Indirect Archetype & Series Support': {'Chimeratech', 'Cybernetic', 'Photon', 'Signature move', 'Toon'},
                        'Competitive Status (TCG Advanced)': 'Unlimited',
                        'Reference': 'https://yugioh.fandom.com/wiki/Cyber_Dragon'}
        assert duelist.add_card(cyber_dragon) == None


    def test_regulatory_checkup(self, duelist):
        correct_card_types = {'Monster', 'Spell', 'Trap'}
        incorrect_competitive_status = {'Legal', 'Not yet released'}
        checkup_df = duelist.regulatory_checkup()
        # Making sure the checkup dataframe contains only incorrect card types or incorrect competitive status
        assert (set(checkup_df['Card Type'].unique()) & correct_card_types == set() or
                set(checkup_df['Competitive Status (TCG Advanced)'].unique()) & incorrect_competitive_status != set())


@pytest.mark.webtest
class TestYgScraper:
    """
    Test Class to handle the unittesting of the YgScraper class in the ygfandom module
    """
    @pytest.mark.parametrize(
        "url, expected_details",
        [('https://yugioh.fandom.com/wiki/Elemental_HERO_Gaia', {'Card Name': 'Elemental HERO Gaia',
                                                                 'Card Type': 'Monster',
                                                                 'Spell/Trap Property': 'N/A',
                                                                 'Attribute': 'EARTH',
                                                                 'Types': 'Warrior / Fusion / Effect',
                                                                 'Level/Rank': '6',
                                                                 'ATK': '2200',
                                                                 'DEF': '2600',
                                                                 'LINK': 'N/A',
                                                                 'Pendulum Scale': 'N/A',
                                                                 'Card Description': '1 "Elemental HERO" monster + 1 EARTH monster. Must be Fusion Summoned and cannot be Special Summoned by other ways. When this card is Fusion Summoned: Target 1 face-up monster your opponent controls; until the End Phase, its ATK is halved and this card gains the same amount of ATK.',
                                                                 'Card/Attribute/Type Support': {'EARTH'},
                                                                 'Direct Archetype & Series Support': {'Elemental HERO', 'HERO'},
                                                                 'Indirect Archetype & Series Support': set(),
                                                                 'Competitive Status (TCG Advanced)': 'Unlimited',
                                                                 'Reference': 'https://yugioh.fandom.com/wiki/Elemental_HERO_Gaia'}),
          ('https://yugioh.fandom.com/wiki/Knightmare_Unicorn', {'Card Name': 'Knightmare Unicorn',
                                                                 'Card Type': 'Monster',
                                                                 'Spell/Trap Property': 'N/A',
                                                                 'Attribute': 'DARK',
                                                                 'Types': 'Fiend / Link / Effect',
                                                                 'Level/Rank': 'N/A',
                                                                 'ATK': '2200',
                                                                 'DEF': 'N/A',
                                                                 'LINK': '3',
                                                                 'Pendulum Scale': 'N/A',
                                                                 'Card Description': '2+ monsters with different names. If this card is Link Summoned: You can discard 1 card, then target 1 card on the field; return it into the Deck, then, if this card was co-linked when this effect was activated, you can draw 1 card. You can only use this effect of "Knightmare Unicorn" once per turn. While any co-linked "Knightmare" monsters is on the field, for your normal draw during your Draw Phase, draw 1 card for each different card name among those co-linked "Knightmare" monsters, instead of drawing just 1 card.',
                                                                 'Card/Attribute/Type Support': set(),
                                                                 'Direct Archetype & Series Support': {'Knightmare'},
                                                                 'Indirect Archetype & Series Support': {'Mekk-Knight'},
                                                                 'Competitive Status (TCG Advanced)': 'Unlimited',
                                                                 'Reference': 'https://yugioh.fandom.com/wiki/Knightmare_Unicorn'}),
          ('https://yugioh.fandom.com/wiki/Astrograph_Sorcerer', {'Card Name': 'Astrograph Sorcerer',
                                                                  'Card Type': 'Monster',
                                                                  'Spell/Trap Property': 'N/A',
                                                                  'Attribute': 'DARK',
                                                                  'Types': 'Spellcaster / Pendulum / Effect',
                                                                  'Level/Rank': '7',
                                                                  'ATK': '2500',
                                                                  'DEF': '2000',
                                                                  'LINK': 'N/A',
                                                                  'Pendulum Scale': '1',
                                                                  'Card Description': 'Pendulum Effect: During your Main Phase: You can destroy this card, and if you do, take 1 "Stargazer Magician" from your hand or Deck, and either place it in your Pendulum Zone or Special Summon it. You can only use this effect of "Astrograph Sorcerer" once per turn. Monster Effect: If a card(s) you control is destroyed by battle or card effect: You can Special Summon this card from your hand, then you can choose 1 monster in the Graveyard, Extra Deck, or that is banished, and that was destroyed this turn, and add 1 monster with the same name from your Deck to your hand. You can banish this card you control, plus 4 monsters from your hand, field, and/or Graveyard (1 each with "Pendulum Dragon", "Xyz Dragon", "Synchro Dragon", and "Fusion Dragon" in their names); Special Summon 1 "Supreme King Z-ARC" from your Extra Deck. (This is treated as a Fusion Summon. )',
                                                                  'Card/Attribute/Type Support': {'Stargazer Magician', 'Supreme King Z-ARC'},
                                                                  'Direct Archetype & Series Support': {'Fusion Dragon', 'Pendulum Dragon', 'Synchro Dragon', 'Xyz Dragon'},
                                                                  'Indirect Archetype & Series Support': {'Four Dimension Dragons', 'Magician', 'Supreme King'},
                                                                  'Competitive Status (TCG Advanced)': 'Forbidden',
                                                                  'Reference': 'https://yugioh.fandom.com/wiki/Astrograph_Sorcerer'})]
    )
    def test_set_get_card_details(self, scraper, url, expected_details):
        scraper.set_card_details(url)
        assert scraper.get_card_details()[0] == expected_details


    @pytest.mark.parametrize(
        "card_set_url, expected_card",
        [('https://yugioh.fandom.com/wiki/Cosmo_Blazer', 'https://yugioh.fandom.com/wiki/Brotherhood_of_the_Fire_Fist_-_Spirit'),
         ('https://yugioh.fandom.com/wiki/Special_Pack_20th_Anniversary_Edition_Vol.5', 'https://yugioh.fandom.com/wiki/Number_38:_Hope_Harbinger_Dragon_Titanic_Galaxy'),
         ('https://yugioh.fandom.com/wiki/Structure_Deck:_Rokket_Revolt', 'https://yugioh.fandom.com/wiki/Dragon_Knight_of_Creation')]
    )
    def test_set_get_card_urls(self, scraper, card_set_url, expected_card):
        scraper.set_card_urls(card_set_url)
        assert expected_card in scraper.get_card_urls()


    @pytest.mark.parametrize(
        "card_url, list_of_card_urls",
        [('https://yugioh.fandom.com/wiki/Polymerization', ['https://yugioh.fandom.com/wiki/Polymerization']),
         (['https://yugioh.fandom.com/wiki/Polymerization', 'https://yugioh.fandom.com/wiki/Polymerization'], ['https://yugioh.fandom.com/wiki/Polymerization']),
         (['https://yugioh.fandom.com/wiki/Polymerization', 'https://yugioh.fandom.com/wiki/Mirror_Force_Launcher'], ['https://yugioh.fandom.com/wiki/Polymerization', 'https://yugioh.fandom.com/wiki/Mirror_Force_Launcher'])
        ]
    )
    def test_add_card_urls(self, scraper, card_url, list_of_card_urls):
        scraper.add_card_urls(card_url)
        assert set(scraper.get_card_urls()) == set(list_of_card_urls)
