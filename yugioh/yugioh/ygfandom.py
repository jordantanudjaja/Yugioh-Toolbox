# -*- coding: utf-8 -*-
"""
Created on Thu Jul 30 18:06:24 2020

Author: Jordan Tanudjaja

Python module for anything related to yugioh in (https://yugioh.fandom.com)
and the 'Yugioh Card Database.csv' file that was initialized on July 29 2020 in this directory.
"""

import pandas as pd
import numpy as np
import requests
from bs4 import BeautifulSoup
import re
import unicodedata

class DbHandler:
    """
    Class for handling and manipulating the yugioh card database
    """
    # Class Variable
    yugioh_columns = ('Card Name', 'Card Type', 'Spell/Trap Property', 'Attribute', 'Types',
                      'Level/Rank', 'ATK', 'DEF', 'LINK', 'Pendulum Scale',
                      'Card Description', 'Card/Attribute/Type Support',
                      'Direct Archetype & Series Support',
                      'Indirect Archetype & Series Support',
                      'Competitive Status (TCG Advanced)', 'Reference')

    def __init__(self, database_filepath = 'Data/Yugioh Card Database.csv'):
        """
        Parameters:
        -----------
        database_filepath: str
            Default value: 'Data/Yugioh Card Database.csv'
            The value has to be in a CSV format, and the default path leads to a
            file that contains all the information of yugioh cards up to the current meta

        Variables:
        ----------
        Public:
            database_filepath: str
                The filepath that leads to the specified Yugioh Card Database

        Private:
            card_database: DataFrame()
                The Yugioh Card Database that is read from the database_filepath
        """
        self.database_filepath = database_filepath
        self.__card_database = pd.read_csv(database_filepath, keep_default_na = False)

    def get_card_database(self):
        """
        Returns the current database file in a DataFrame format
        """
        return self.__card_database

    def set_card_database(self, df):
        """
        Set method that sets the yugioh card database with a dataframe as its argument. It is used
        to reflect any outside changes made to the database when assigning the database to
        any outside variables in the first place

        Parameters:
        -----------
        df: DataFrame
            The value has to be in a dataframe format, and it has to be yugioh related
        """
        class InvalidDataFrameError(Exception):
            def __init__(self, message):
                print(message)

        # Block of code to make sure the user input a dataframe that follows the Yugioh Card Database format
        if tuple(df.columns) != DbHandler.yugioh_columns or len(df) < 10391:
            raise InvalidDataFrameError('DataFrame is invalid and cannot be set as the Yugioh Card Database')
        else:
            self.__card_database = df

    def save_card_database(self):
        """
        Method to save the database to the name of the csv file that was initialized at the start
        of instantiation
        """
        # Required to set index to Card Name before writing to the csv file in order to prevent insertion
        # of additonal Unnamed columns when reading the csv file in get_card_database()
        self.__card_database.set_index('Card Name').to_csv(self.database_filepath)
        print('Save successful')

    def search_card_name(self, name):
        """
        Returns a dataframe of the cards that were searched, if the cards are not in the database,
        of if there are errors in spelling, it will print out the name of the card that was erroneous

        Parameters:
        -----------
        name: str or list
            name or names of the cards that are meant to be searched
        """
        df = self.__card_database.copy() # Since there will be some changes to df, it is important
                                         # to set a copy to prevent the changes from affecting the original database
                                         # pandas are passed by referenced by default after all

        # Converting the card names to lowercase to allow the user to input lower case letters without throwing an error
        df['Card Name'] = df['Card Name'].apply(lambda x: x.lower())
        if type(name) == str:
            name = [name.lower()]
        else:
            name = list(set(map(lambda x: x.lower(), name)))

        while True:
            try:
                indexes_to_search = []
                for n in name:
                    name_tracker = n
                    indexes_to_search.append(df.set_index('Card Name').index.get_loc(n))
            except KeyError as e:
                print(f'{e} is not in database, make sure you check your spellings, and cross-reference with the database using locate_card method')
                if len(name) == 1:
                    return pd.DataFrame(columns = DbHandler.yugioh_columns) # Returning empty dataframe with yugioh columns
                else:
                    name.remove(name_tracker) # Removing the erroneous card name
            else:
                return self.__card_database.iloc[indexes_to_search].sort_index()

    def locate_card(self, card_url):
        """
        Returns the current index of a specific card that already resides in the database, and returns
        nothing if the card does not exist

        Parameters:
        ----------
        card_url: str
            The card url has to be from https://yugioh.fandom.com and has to be a card URL, not a booster
            pack URL or a deck URL
        """
        df = self.__card_database
        if df[df['Reference'] == card_url].index.size != 0:
            card_index = df[df['Reference'] == card_url].index[0]
            print(f"{df['Card Name'].iloc[card_index]} is already in the Yugioh database and it is located at index: {card_index}")
            return card_index
        else:
            print('Card is not in database')
            return None

    def add_card(self, card_dict):
        """
        Returns the updated database after a successful addition of a new card, otherwise, it will not
        return anything

        Parameters:
        ----------
        card_dict: dict
            The card has to be in the dictionary format and thus the method, get_card_details, in the
            YgScraper class has to be invoked on the specific card url first and return the value to
            a local variable before invoking this method
        """
        list_of_keys = ['Card Name', 'Card Type', 'Spell/Trap Property', 'Attribute', 'Types', 'Level/Rank',
                        'ATK','DEF', 'LINK', 'Pendulum Scale', 'Card Description', 'Card/Attribute/Type Support',
                        'Direct Archetype & Series Support', 'Indirect Archetype & Series Support', 'Competitive Status (TCG Advanced)', 'Reference']

        if (type(card_dict) != dict) or (set(card_dict.keys()).union(set(list_of_keys)) != set(list_of_keys)):
            raise Exception('The card format passed is not correct, make sure you call YgSraper.get_card_details on the URL first')
        else:
            if self.locate_card(card_dict['Reference']) == None:
                self.__card_database = self.__card_database.append(card_dict, ignore_index = True)
                print(f"{card_dict['Card Name']} is successfully added")
                self.save_card_database()
                return self.__card_database
            else:
                print(f"{card_dict['Card Name']} was not added into the database")

    def regulatory_checkup(self):
        """
        Returns a dataframe that consist of cards that needs to be updated in the database or contain
        erroneous values

        Errors are reflected in the Card Type column. If the Card Type of any card is not Monster, Spell
        or Trap, then some kind of error is found when adding that card to the database
        """
        df = self.__card_database

        # Dataframe that contains a list of cards with errors when they were added to the database or
        # cards that have status: Not yet released and needs to be updated
        checkup_df = df[(df['Card Type'] != 'Monster') & (df['Card Type'] != 'Spell') & (df['Card Type'] != 'Trap')
                      | (df['Competitive Status (TCG Advanced)'] == 'Legal')
                      | (df['Competitive Status (TCG Advanced)'] == 'Not yet released')]

        if checkup_df.index.size == 0:
            print('No updates needed')
        else:
            print('Some updates needed')
        return checkup_df


class YgScraper:
    """
        Class for scraping the https://yugioh.fandom website to get the URLs for cards from card sets URLs
        and translating the information to a readable format
    """
    def __init__(self):
        """
        Variables:
        ---------
        Public:
            card_url_list: list
                Holds the list of card URLs interested in scraping

        Private:
            card_details = list of dictionaries
                Holds the list of card details that were scraped from the urls in card_url_list, each card
                detail is in the format of a dictionary
        """
        self.card_url_list = []
        self.__card_details = []


    def __atk_def_link_parser(self, atk_def_link):
        """
        Returns a tuple of the (ATK, DEF/LINK) property of a yugioh monster card

        Private method that is invoked in the set_card_details method

        Parameters:
        ----------
        atk_def_link : str
            The ATK/DEF or ATK/LINK property of a yugioh monster card, it is passed as a string value
            during the scraping process
        """
        pattern_atk = r'^\w*\?*'
        pattern_def_link = r'\w*\?*$'

        # re.match only checks for a match at the beginning of the string, but it is quicker than search
        try:
            ATK = int(re.match(pattern_atk, atk_def_link).group(0))
        except (ValueError):
            ATK = re.match(pattern_atk, atk_def_link).group(0)

        # re.search checks for a match anywhere in the string
        try:
            DEF_LINK = int(re.search(pattern_def_link, atk_def_link).group(0))
        except ValueError:
            DEF_LINK = re.search(pattern_def_link, atk_def_link).group(0)

        return (ATK, DEF_LINK)


    def set_card_details(self, url):
        """
        Set method that scrapes the card url in its argument and sets the details of the card to a
        dictionary in a user-readable format

        Parameters:
        -----------
        url: str
            This is the individual card url, each card url in https://yugioh.fandom follows a
            more or less similar format that can be scraped using the algorithm below
        """

        if url not in self.card_url_list:
            self.card_url_list.append(url)

        # Try-block code to read the table in the card url, and if the url passed is not a card URL,
        # the except-block will run and print out that url that is faulty
        try:
            card_details_df = pd.read_html(url, attrs = {'class': "cardtable"})[0]
        except ValueError:
            print(url)
            return None
        else:
            card_details_df.drop(columns = [card_details_df.columns[0]], inplace = True)
            card_details_df.rename(columns = {card_details_df.columns[1]: 'Card Properties'}, inplace = True)
            card_details_df.set_index(card_details_df.columns[0], inplace = True)

            # Variables of the Yugioh cards I am interested in
            card_name = 'N/A'
            card_type = 'N/A'
            spell_trap_property = 'N/A'
            attribute = 'N/A'
            types = 'N/A'
            level_rank = 'N/A'
            ATK = 'N/A'
            DEF = 'N/A'
            LINK = 'N/A'
            pendulum_scale = 'N/A'
            card_description = 'N/A'
            card_attribute_type_support = set()
            direct_archetype_series_support = set()
            indirect_archetype_series_support = set()
            competitive_status = 'N/A'

            # Try block to handle the card information, and any errors that occur
            # Some cards may have careless mistakes that or missing information that is not in the norm and impossible
            # to check the specific error encountered
            try:
                # Block of code to handle Card Names
                # Some cards have multiple English indexes, and so their names are a series of anything with
                # the English index, and this if else block of code helps to separate the true english
                # name from all other values in that index
                if isinstance(card_details_df['Card Properties'].loc['English'], str):
                    card_name = card_details_df['Card Properties'].loc['English']
                else:
                    card_name = card_details_df['Card Properties'].loc['English'][0]

                # Block of code to handle Card Types (Monster, Spell, Trap)
                card_type = card_details_df['Card Properties'].loc['Card type']

                if card_details_df['Card Properties'].loc['Card type'] != 'Monster': # Block of code to handle spell and trap cards
                    spell_trap_property = card_details_df['Card Properties'].loc['Property']
                else: # Block of code to handle monster cards
                    attribute = card_details_df['Card Properties'].loc['Attribute']

                    try:
                        types = card_details_df['Card Properties'].loc['Type'] + ' / Normal'
                    except KeyError:
                        types = card_details_df['Card Properties'].loc['Types']

                    # Try-Block to handle level/rank discrepancies of Xyz and non-Xyz Monsters
                    try:
                        level_rank = int(card_details_df['Card Properties'].loc['Level'])
                    except KeyError:
                        try:
                            level_rank = int(card_details_df['Card Properties'].loc['Rank'])
                        except KeyError: # For Link Monsters with no level or rank
                            level_rank = 'N/A'

                    # Try-Block to handle ATK, DEF, and LINK discrepancies of LINK and non-LINK monsters
                    try:
                        atk_def_link = card_details_df['Card Properties'].loc['ATK / DEF']
                        DEF = self.__atk_def_link_parser(atk_def_link)[1]
                        LINK = 'N/A'
                    except KeyError:
                        atk_def_link = card_details_df['Card Properties'].loc['ATK / LINK']
                        LINK = self.__atk_def_link_parser(atk_def_link)[1]
                        DEF = 'N/A'
                    finally:
                        ATK = self.__atk_def_link_parser(atk_def_link)[0]

                    # Try-Block to handle the properties of Pendulum Monsters
                    try:
                        pendulum_scale = int(card_details_df['Card Properties'].loc['Pendulum Scale'])
                    except KeyError:
                        pendulum_scale = 'N/A'

                # Block of code to handle the card description of all cards and make them readable
                source = requests.get(url)
                if source.status_code == 200:
                    site_html = BeautifulSoup(source.text.encode('utf-8'), 'html.parser')
                uncleaned_description = unicodedata.normalize("NFKD", site_html.find_all('td', attrs = {'class': "navbox-list"})[0].text.replace('\n', ''))
                card_description = re.sub(r'(?<=[.,])(?=[^\s])', r' ', uncleaned_description) # Pendulum Monsters text have this issue
                card_description = re.sub(r'(?<=[a-z])(?=[A-Z])', '. ',  card_description) # Link and Synchro Monsters have this issue
                card_description = re.sub(r'(?<=[a-z]["])(?=[A-Z])', r'. ', card_description) # Fusion monsters text have this issue

                # Block of code to handle which archetype/series/attribute/type/individual cards that each card supports
                if site_html.find('div', attrs = {'class': "hlist"}).dt:
                    for div in site_html.find_all('div', attrs = {'class': "hlist"}):
                        try:
                            if div.dt.text.replace('\n', '').strip() == 'Supports':
                                for dd in div.find_all('dd'):
                                    card_attribute_type_support.add(dd.text.replace('\n', '').strip())
                            elif div.dt.text.replace('\n', '').strip() == 'Archetypes and series' or div.dt.text.replace('\n', '').strip() == 'Supports archetypes':
                                for dd in div.find_all('dd'):
                                    direct_archetype_series_support.add(dd.text.replace('\n', '').strip())
                            elif div.dt.text.replace('\n', '').strip() == 'Related to archetypes and series':
                                for dd in div.find_all('dd'):
                                    indirect_archetype_series_support.add(dd.text.replace('\n', '').strip())
                            else:
                                break
                        except AttributeError:
                            break
                else:
                    pass

                # Block of code to handle the competitive status of each card in the current TCG Advanced meta
                pattern_to_search = 'TCG Advanced'
                pattern_to_extract = r'^\w+'
                if isinstance(card_details_df['Card Properties'].loc['Statuses'], str):
                    competitive_status = card_details_df['Card Properties'].loc['Statuses']
                    if re.search(pattern_to_search, competitive_status):
                        competitive_status = re.match(pattern_to_extract, competitive_status).group()
                    else:
                        pass
                else:
                    for status in card_details_df['Card Properties'].loc['Statuses'].values:
                        if re.search(pattern_to_search, status):
                            competitive_status = re.match(pattern_to_extract, status).group()

            except Exception as e:
                card_type = e

            # Putting all the card informations in a dictionary format
            card_dict = {
                'Card Name': card_name,
                'Card Type': card_type,
                'Spell/Trap Property': spell_trap_property,
                'Attribute': attribute,
                'Types': types,
                'Level/Rank': str(level_rank),
                'ATK': str(ATK),
                'DEF': str(DEF),
                'LINK': str(LINK),
                'Pendulum Scale': str(pendulum_scale),
                'Card Description': card_description,
                'Card/Attribute/Type Support': card_attribute_type_support,
                'Direct Archetype & Series Support': direct_archetype_series_support,
                'Indirect Archetype & Series Support': indirect_archetype_series_support,
                'Competitive Status (TCG Advanced)': competitive_status,
                'Reference': url,
                }

            self.__card_details.append(card_dict)

    def get_card_details(self):
        """
        Returns the card details in a list format from the set_card_details method
        """
        self.__card_details = [i for n, i in enumerate(self.__card_details) if i not in self.__card_details[n + 1:]]  # To remove duplicate cards
        return self.__card_details

    def set_card_urls(self, card_set_url):
        """
        Set method that scrapes a card set URL (packs, decks, reprint sets, tins) and sets all the urls of
        each card from the card set in a list format to the object variable, card_url_list

        This is an automatic way of getting the card urls of cards in a set rather than appending each
        individual card urls to the list one by one

        Parameters:
        -----------
        card_set_url: str
            The url of the card set, it has to be a card set, and not an individual card
        """
        card_set_source = requests.get(card_set_url)

        if card_set_source.status_code == 200:
            card_set_html = BeautifulSoup(card_set_source.text.encode('utf-8'), 'html.parser')

        class_or_id = 'class'
        attribute_name = "wikitable"
        # Code hacks for 2 card pack URLs
        if card_set_url == 'https://yugioh.fandom.com/wiki/Duelist_Pack:_Kite':
            attribute_name = "sortable"
        elif card_set_url == 'https://yugioh.fandom.com/wiki/Collection_Pack_2020':
            class_or_id = 'id'
            attribute_name = 'Top_table'

        card_url_list = []

        for card_table in card_set_html.find_all('table', attrs = {class_or_id: attribute_name}):
            # Building a table of hyperlinks because pd.read_html does not read the hyperlinks, but only reads the unlinked
            # text of tables
            record = list()
            for tr in card_table.findAll("tr"):
                ths = tr.findAll("th")
                if ths != []:
                    columns = [th.text.replace('\n', '').strip() for th in ths]
                else:
                    row = list()
                    for td in tr.find_all('td'):
                        try:
                            row.append(td.a['href'])
                        except KeyError:
                            row.append(td.a.text)
                        except TypeError:
                            row.append(td.text)
                    record.append(row)

            card_set_df = pd.DataFrame(data = record, columns = columns)
            try:
                card_set_df.rename(columns = {'English name': 'Card Name'}, inplace = True)
                # Raise keyword is used because KeyError was handled previously above, thus raise is
                # needed to  reraise the KeyError if it comes up again
                raise KeyError()
            except KeyError:
                card_set_df.rename(columns = {'Name': 'Card Name'}, inplace = True)
            finally:
                # Filtering out the links with no 'wiki' in them, all legit cards in the yugioh fandom site has wiki in their urls
                card_set_df['Card Name'] = card_set_df['Card Name'].apply(lambda x: np.where(x.find('wiki') != -1, x, 'Not a link'))
                card_set_df = card_set_df[card_set_df['Card Name'] != 'Not a link']
                # Adding yugioh.fandom in front of the link to complete the URL
                card_set_df['Card Name'] = card_set_df['Card Name'].apply(lambda x: 'https://yugioh.fandom.com' + x)
                card_url_list.extend(list(card_set_df['Card Name']))

        self.card_url_list.extend(list(set(card_url_list)))

        # Automatically adding the card details of each card in card url list to the card_details instance variable
        # for link in self.card_url_list:
        #     try:
        #         self.set_card_details(link)
        #     except:
        #          print(f'Check the url again {link} and see if there is anything fishy')
        #          pass

    def add_card_urls(self, urls):
        """
        Method that adds any specified card urls to the current card_url_list

        Parameters:
        -----------
        urls: str or list of strings
            Indiviual card url or multiple urls to be added into the current card_url_list
        """
        if type(urls) == str:
            urls = [urls]
        self.card_url_list.extend(urls)
        self.card_url_list = list(set(self.card_url_list))
        # for link in self.card_url_list:
        #     try:
        #         self.set_card_details(link)
        #     except:
        #          print(f'Check the url again {link} and see if there is anything fishy')
        #          pass


    def get_card_urls(self):
        """
        Returns the list of card urls that was initialized or added from the set_card_urls method
        """
        self.card_url_list = list(set(self.card_url_list)) # To remove duplicate urls
        return self.card_url_list
