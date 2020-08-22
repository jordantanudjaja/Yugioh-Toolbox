# -*- coding: utf-8 -*-
"""
Created on Fri Aug 21 12:03:34 2020

Author: Jordan Tanudjaja

Unit-testing Module for banlist.py
To be called with python -m pytest in the command line because pytest does not work since I did not
create this in development mode in a virtual environment
"""

from yugioh import banlist, ygfandom as ygf
import requests
from bs4 import BeautifulSoup
import pytest


@pytest.fixture(scope = 'module')
def duelist():
    duelist = ygf.DbHandler(database_filepath = '../../Data/Yugioh Card Database.csv')
    duelist.database_filepath = '../../Data/Yugioh Card Database (Testing).csv'
    return duelist

@pytest.mark.webtest
def test_banlist_update(duelist, monkeypatch):
    """
    Test Function to handle the banlist_update function in the banlist module
    """    
    banlist_source = requests.get('https://www.yugioh-card.com/uk/gameplay/detail.php?id=1155')
    assert banlist_source.status_code == 200 # Ensuring the website can be accessed successfully
    
    banlist_source_html = BeautifulSoup(banlist_source.text.encode('utf-8'), 'html.parser')
   
    def mock_banlist_update(banlist_source_html):
        """
        A mock of the banlist_update function to test only the essential parts of the function and
        not the entire function itself
        """
        # Creating 2 temporary lists, banlist cards contain the names of the cards in the banlist
        # update_status contains the current competitive status of those cards
        banlist_cards = []
        uptodate_status = []
        banlist_card_names = set()
        unique_card_status = set()
        
        for tr in banlist_source_html.find_all('tr'):
            banlist_cards.append([td.text for td in tr.find_all('td', attrs = {'class': 'xl763'})])
            uptodate_status.append([td.text for td in tr.find_all('td', attrs = {'class': 'xl753'})])
        
        # Editing the lists to combine card names and statuses into the banlist_card list
        for i in range(len(banlist_cards)):
            if len(banlist_cards[i]) != 0:
                banlist_cards[i][1] = uptodate_status[i][1]    
        
        for card in banlist_cards:
            if len(card) != 0:
                banlist_card_names.add(card[0])
                unique_card_status.add(card[1])
        
        return (banlist_card_names, unique_card_status)

    monkeypatch.setattr(banlist, 'banlist_update', mock_banlist_update) # Monkeypatching the banlist_update to the mocked function
    
    db_card_names = set(duelist.get_card_database()['Card Name'])
    db_competitive_status = set(duelist.get_card_database()['Competitive Status (TCG Advanced)'])
    
    banlist_card_names = banlist.banlist_update(banlist_source_html)[0]
    unique_card_status = banlist.banlist_update(banlist_source_html)[1]
    
    # Ensuring that the data scraped from the website has some card names in the database, which shows
    # that the banlist_update algorithm is working      
    assert banlist_card_names & db_card_names != set()
    assert unique_card_status & db_competitive_status != set()