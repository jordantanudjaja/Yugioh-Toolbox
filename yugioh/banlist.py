# -*- coding: utf-8 -*-
"""
Created on Mon Aug 10 21:58:33 2020

Author: Jordan Tanudjaja

Python module for Banlist-related things in the yugioh metagame. The module interacts with the
Yugioh Card Database from the ygfandom module. Banlist source is taken from 
(https://www.yugioh-card.com/uk/gameplay/detail.php?id=1155)
"""

import requests
from bs4 import BeautifulSoup
import textdistance
from yugioh import ygfandom as ygf

def banlist_update(banlist_url = 'https://www.yugioh-card.com/uk/gameplay/detail.php?id=1155', duelist = ygf.DbHandler()):
    """
    Method used to update the database with the up to date competitive status of cards in the banlist

    The method scrapes the data from the URL and cross-references it with the competitve status of the
    cards in the current database, and updates them accordingly

    Bug: Some of the cards in this URL are not fully scraped by the method

    Parameters:
    -----------
    banlist_url: str
        Default value: 'https://www.yugioh-card.com/uk/gameplay/detail.php?id=1155'
        
        URL that contains the most recent banlist, and this method only works with the above URL and no
        other URL
        
    duelist: DbHandler()
        Default value: DbHandler(database_filepath = 'yugioh/Data/Yugioh Card Database.csv')
            
        User-defined object from the ygfandom module that accesses the Yugioh Card Database
    """
    # url for accessing the current banlist
    # read_html does not work for this website, hence we have to manually scrape the table for information
    banlist_source = requests.get(banlist_url)

    if banlist_source.status_code == 200:
        banlist_source_html = BeautifulSoup(banlist_source.text.encode('utf-8'), 'html.parser')

    # Creating 2 temporary lists, banlist cards contains the names of the cards in the banlist
    # update_status contains the current competitive status of those cards
    banlist_cards = list()
    uptodate_status = list()

    for tr in banlist_source_html.find_all('tr'):
        banlist_cards.append([td.text for td in tr.find_all('td', attrs = {'class': 'xl763'})])
        uptodate_status.append([td.text for td in tr.find_all('td', attrs = {'class': 'xl753'})])

    # Editing the lists to combine card names and statuses into the banlist_card list
    for i in range(len(banlist_cards)):
        if len(banlist_cards[i]) != 0:
            banlist_cards[i][1] = uptodate_status[i][1]

    df = duelist.get_card_database()

    # Block of code for checking the status of the current cards in the database and cross-referencing to
    # the banlist
    for card in banlist_cards:
        if len(card) != 0:
            try:
                if card[0] in df['Card Name'].values:
                    db_name = df[df['Card Name'] == card[0]]['Card Name'].iloc[0]
                else:
                    df['txtdistance'] = df['Card Name'].apply(lambda x: textdistance.levenshtein(card[0], x))
                    db_name = df[df['txtdistance'] <= 2]['Card Name'].iloc[0]
                    df.drop(columns = ['txtdistance'], inplace = True)

                if df[df['Card Name'] == db_name]['Competitive Status (TCG Advanced)'].iloc[0] == card[1]:
                    print(f"{db_name}'s status is the same ({card[1]}), no change needed")
                elif card[1] == 'No longer on list':
                    if df[df['Card Name'] == db_name]['Competitive Status (TCG Advanced)'].iloc[0] != 'Unlimited':
                        df['Competitive Status (TCG Advanced)'].loc[df[df['Card Name'] == db_name].index] = 'Unlimited'
                        print(f"{db_name}'s status is changed to Unlimited")
                else:
                    df['Competitive Status (TCG Advanced)'].loc[df[df['Card Name'] == db_name].index] = card[1]
                    print(f"{db_name}'s status is changed to {card[1]}")
            except:
                print(f'{card[0]} was not found in database, use locate_card method to check if the card is actually in the database')

    duelist.set_card_database(df)
    duelist.save_card_database()

    return df


