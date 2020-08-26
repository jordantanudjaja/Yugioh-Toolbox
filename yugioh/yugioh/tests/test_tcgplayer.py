# -*- coding: utf-8 -*-
"""
Created on Fri Aug 21 20:44:52 2020

Author: Jordan Tanudjaja

Unit-testing Module for tcgplayer.py
To be called with python -m pytest in the command line because pytest does not work since I did not
create this in development mode in a virtual environment
"""

from yugioh import tcgplayer as tcg
import pytest

@pytest.fixture(scope = 'module')
def card_bundle():
    card_bundle = tcg.CardPriceScraper(PATH = '../../External Applications/chromedriver.exe', filepath = '../../Data/Yugioh Card Database.csv')
    return card_bundle

@pytest.mark.seleniumtest
class TestCardPriceSraper:
    """
    Test Class to handle the CardPriceScraper Class in the tcgplayer module
    """
    def test_webpage(self, card_bundle):
        assert card_bundle.driver.title == 'TCGplayer.com: Online Store for Magic: The Gathering, Yugioh, Cards, Sets, Packs, and Booster Boxes'


    @pytest.mark.parametrize(
    "card_names, expected_results",
    [('Cyber Dragon', 1),
     ('cyBeR dRagON', 1),
     ('sdgsag', 0),
     (['DarK siMOrgH', 'MaxX "C"', 'sdgl'], 2),
     (['cYbeR DraGOn', 'Cyber Dragon', 'DaRK magician'], 2)]
    )
    def test_check_card_names(self, card_bundle, card_names, expected_results):
        assert len(card_bundle.check_card_names(card_names, filepath = '../../Data/Yugioh Card Database.csv')) == expected_results


    def test_price_searcher(self, card_bundle, monkeypatch):
        assert card_bundle.driver.find_element_by_id('autocomplete-input')
        assert card_bundle.price_searcher('cybEr drAGon') != {}
        assert card_bundle.price_searcher('sdgsdg') == {}


    def test_set_get_card_prices_combined_df(self, card_bundle):
        with pytest.raises(KeyError) as error:
            card_bundle.set_card_prices('sdgsd')
        assert str(error.value) == "'This card you inputted is not in the database!'"
        card_bundle.set_card_prices('cYber DraGON')
        assert len(card_bundle.get_card_prices()) == 1
        assert len(card_bundle.get_combined_df()) == 1


    def test_quit_browser(self, card_bundle):
        card_bundle.quit_browser()
        with pytest.raises(Exception) as error:
            card_bundle.quit_browser()
        assert str(error.value) == 'Browser is already closed, unable to quit browser that is no longer open'


    def test_restart_browser(self, card_bundle):
        card_bundle.restart_browser()
        assert card_bundle.driver.current_url == 'https://www.tcgplayer.com/'
        card_bundle.price_searcher('sdgsdg')
        card_bundle.restart_browser()
        assert card_bundle.driver.current_url == 'https://www.tcgplayer.com/'


@pytest.fixture(scope = 'module')
def shopping_cart():
    shopping_cart = tcg.BuyingTool([('Cyber Dragon', 3)], PATH = '../../External Applications/chromedriver.exe', filepath = '../../Data/Yugioh Card Database.csv')
    return shopping_cart

@pytest.mark.seleniumtest
class TestBuyingTool:
    def test_set_get_buying_prices_dfs(self, shopping_cart):
        assert len(shopping_cart.get_normalprice_df()) == 1
        assert len(shopping_cart.get_totalprice_df()) == 1
        assert len(shopping_cart.get_cumulative_df()) == 1

        with pytest.raises(KeyError) as error:
            shopping_cart.set_buying_dfs([('gsdg', 2)])
            assert str(error.value) == 'Check the spelling of your card!'
        assert shopping_cart.get_normalprice_df() == None
        assert shopping_cart.get_totalprice_df() == None
        assert shopping_cart.get_cumulative_df() == None


    def test_add_to_cart(self, shopping_cart):
        shopping_cart.add_to_cart([('dark MagicIAn', 4), ('dark SimORgh', 7)])
        assert len(shopping_cart.get_normalprice_df()) == 2
        assert len(shopping_cart.get_totalprice_df()) == 2
        assert len(shopping_cart.get_cumulative_df()) == 1
        assert shopping_cart.get_normalprice_df()['Quantity'].loc['Dark Magician'] == 4
        assert shopping_cart.get_cumulative_df()['Total no. of cards'].loc['Cumulative Total'] == 11

        shopping_cart.add_to_cart([('khjn', 4), ('cyBer drAgon', 4)])
        assert len(shopping_cart.get_normalprice_df()) == 3
        assert len(shopping_cart.get_totalprice_df()) == 3
        assert len(shopping_cart.get_cumulative_df()) == 1
        assert shopping_cart.get_normalprice_df()['Quantity'].loc['Cyber Dragon'] == 4
        assert shopping_cart.get_cumulative_df()['Total no. of cards'].loc['Cumulative Total'] == 15

        shopping_cart.add_to_cart([('DARK SIMORGH', 3)])
        assert shopping_cart.get_normalprice_df()['Quantity'].loc['Dark Simorgh'] == 10
        assert shopping_cart.cards_dict == {'dark magician': 4, 'dark simorgh': 10, 'cyber dragon': 4}


    def test_remove_from_cart(self, shopping_cart):
        shopping_cart.remove_from_cart([('DarK SiMoRGH', 5)])
        assert shopping_cart.cards_dict == {'dark magician': 4, 'dark simorgh': 5, 'cyber dragon': 4}
        assert shopping_cart.get_normalprice_df()['Quantity'].loc['Dark Simorgh'] == 5

        shopping_cart.remove_from_cart([('slgks', 2), ('CyBER DraGoN', 89)])
        assert shopping_cart.cards_dict == {'dark magician': 4, 'dark simorgh': 5}
        assert len(shopping_cart.get_normalprice_df()) == 2
        assert len(shopping_cart.get_totalprice_df()) == 2
        assert shopping_cart.get_cumulative_df()['Total no. of cards'].loc['Cumulative Total'] == 9
