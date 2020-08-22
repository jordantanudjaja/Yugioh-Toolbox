# -*- coding: utf-8 -*-
"""
Created on Mon Aug 10 16:48:13 2020

Author: Jordan Tanudjaja

Python module for searching card prices in (https://www.tcgplayer.com), collecting data
and cross-referencing with the Yugioh Card Database in the Data directory
"""

import pandas as pd
import time
from yugioh import ygfandom as ygf

# Selenium imports
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class CardPriceScraper:
    """
    Class that scrapes the https://www.tcgplayer.com website and manipulates the site using
    Selenium to return the prices of whatever card the user is interested in looking at
    """
    def __init__(self, PATH = 'External Applications/chromedriver.exe'):
        """
        Parameters:
        -----------
        PATH: str
            Default value: 'External Applications/chromedriver.exe'

            File path for the chromedriver executable file

        Variables:
        ----------
        Public:
            driver: webdriver.Chrome()
                The driver that opens the Chrome browser from the Selenium Package

        Private:
            card_prices_df: DataFrame()
                Dataframe that provides a list of price statistics for specified cards

            combined_df: DataFrame()
                Dataframe that merges the card_prices_df and a subset of the yugioh card database
                that includes the columns: Card Type, Competitive Status, and Reference
        """
        self.driver = webdriver.Chrome(executable_path = PATH)
        self.driver.get('https://www.tcgplayer.com/')
        self.__card_prices_df = pd.DataFrame()
        self.__combined_df = pd.DataFrame()

    @staticmethod
    def check_card_names(card_names, filepath = 'Data/Yugioh Card Database.csv'):
        """
        Returns a dataframe that consists of cards specified by card names and the Card Type,
        Competitive Status and Reference columns of the Yugioh Card Database if they exist in the
        database. If not, it returns an empty DataFrame

        Static method to check the names of cards that are inputted and making sure they exist in
        the Yugioh Card Database

        Parameters:
        -----------
        card_names: str or list
            The name(s) of the cards that are to be searched and compared with the Yugioh Card Database.
            Punctuation, and spelling matters but not upper or lower case letters

        filepath: str
            Default value: 'Data/Yugioh Card Database.csv'

            Filepath that leads to the Yugioh Card Database to initialize a DbHandler Object. Default
            value allows any python file in the same level as the yugioh package to access the database
            directly. The method, search_card_name, from the object is invoked here
        """
        if type(card_names) == str:
            card_names = [card_names] # Converting it to a list
        card_names = list(set(card_names))
        duelist = ygf.DbHandler(database_filepath = filepath)
        tosearch_df = duelist.search_card_name(card_names)[['Card Name', 'Card Type', 'Competitive Status (TCG Advanced)', 'Reference']]
        return tosearch_df

    def price_searcher(self, db_card_name):
        """
            Returns a dictionary of price statistics of the card that has the same name as db_card_name
            in the web page

            Parameters:
            -----------
            db_card_name: str
                card name of the card to be searched
        """
        search = self.driver.find_element_by_id('autocomplete-input')
        search.send_keys(db_card_name)
        search.send_keys(Keys.RETURN)

        try:
            # finding the number of results that appears at the bottom of the page
            # because that takes the longest to load
            results = WebDriverWait(self.driver, 3).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'results'))
            )
        except:
            self.driver.quit()
            print(f'{db_card_name} is not found in tcgplayer.com')
            return None
        else:
            time.sleep(1) # Pausing script here for 1 second because the script moves too fast before
                          # the web page can even load

        # card_info shows the list of all cards in the page and only searching this 1 page,
        # the code does not go into the next page eventhough there are cards in the next page
        card_info = self.driver.find_elements_by_class_name('search-result__content')

        market_price_list = []
        lowest_price_list = []
        for card in card_info:
            name = card.find_element_by_class_name('search-result__title').text
            if name.lower() == db_card_name.lower():
                try:
                    market_price = card.find_element_by_class_name('search-result__market-price--value').text
                    lowest_price = card.find_element_by_class_name('inventory__price-with-shipping').text
                except:
                    pass
                else:
                    market_price_list.append(float(market_price.strip('$').replace(',', '')))
                    lowest_price_list.append(float(lowest_price.strip('$').replace(',', '')))
        all_price_list = market_price_list + lowest_price_list

        price_stats = {}
        try:
            avg_mkt_price = round(sum(market_price_list) / len(market_price_list), 2)
            avg_lowest_price = round(sum(lowest_price_list) / len(lowest_price_list), 2)
            cheapest_price = round(min(all_price_list), 2)
            highest_price = round(max(all_price_list), 2)
        except ZeroDivisionError:
            print('Your input is probably spelled incorrectly or there are actually no sellers selling that card')
        else:
            price_stats = {'Average Market Price': avg_mkt_price,
                           'Average Lowest Price': avg_lowest_price,
                           'Cheapest Price': cheapest_price,
                           'Highest Price': highest_price}
        finally:
            search.send_keys(Keys.CONTROL + 'a')
            search.send_keys(Keys.DELETE)

            return price_stats


    def set_card_prices(self, card_names, filepath = 'Data/Yugioh Card Database.csv'):
        """
        Set method that sets the card prices of the card names to be searched into a dataframe format
        for readability and also sets a combined dataframe that merges the card price dataframe with
        the subset of yugioh card database with columns: Card Type, Competitive Status, Reference

        Parameters:
        -----------
        card_names: str or list
            The name(s) of the cards that are to be searched and compared with the Yugioh Card Database.
            Punctuation, upper and lower case letters, and spelling matters

        filepath: str
            Default value: 'Data/Yugioh Card Database.csv'

            Filepath that leads to the Yugioh Card Database. Default value allows any python file in the
            same level as the yugioh package to access the database directly
        """
        tosearch_df = self.check_card_names(card_names, filepath)

        if len(tosearch_df) == 0:
            raise KeyError('This card you inputted is not in the database!')
        else:
            card_prices = {}
            for name in tosearch_df['Card Name'].unique():
                card_prices[name] = self.price_searcher(name)

            self.__card_prices_df = pd.DataFrame.from_dict(card_prices, orient = 'index')
            self.__combined_df = ( tosearch_df.merge(self.__card_prices_df,
                                                    left_on = tosearch_df['Card Name'],
                                                    right_on = self.__card_prices_df.index,
                                                    how = 'left')
                                              .drop(columns = ['key_0'])
                                              .set_index('Card Name') )


    def get_card_prices(self):
        """
        Returns the card prices dataframe that only shows the price statistics of each card
        that was successfully searched
        """
        return self.__card_prices_df

    def get_combined_df(self):
        """
        Returns the combined dataframe of the card prices dataframe and the subset of Yugioh Card
        Database with columns: Card Type, Competitive Status, Reference
        """
        return self.__combined_df

    def quit_browser(self):
        """
        Method to quit the current browser

        WARNING: User cannot invoke the price_searcher method and set_card_prices method if the
        browswer is closed. The restart_browser method will have to be invoked first to open
        the browser again
        """
        try:
            self.driver.get('https://www.tcgplayer.com')
        except:
            raise Exception('Browser is already closed, unable to quit browser that is no longer open')
            #print('Browser is already closed, unable to quit browser that is no longer open')
        else:
            try:
                # Waiting for a certain content page to appear to bypass the broken pipe error
                content = WebDriverWait(self.driver, 3).until(
                    EC.presence_of_element_located((By.CLASS_NAME, 'homepage-content'))
                )
            except:
                self.driver.quit()
            else:
                self.driver.quit()

    def restart_browser(self):
        """
        Method to restart the browser if it is closed or refreshes the page to the url:
        https://www.tcgplayer.com from any url that it is currently in
        """
        try:
            self.driver.get('https://www.tcgplayer.com/')
        except:
            self.driver = webdriver.Chrome('C:\Program Files (x86)\Google\Chrome\Application\chromedriver.exe')
            self.driver.get('https://www.tcgplayer.com/')


class BuyingTool(CardPriceScraper):
    """
    Child class of CardPriceScraper that serves as an interface to return various price statistics
    of cards that the user is trying to buy based on the quantity of each card that is going to
    be purchased
    """
    def __init__(self, cards_to_buy, PATH = 'External Applications/chromedriver.exe', filepath = 'Data/Yugioh Card Database.csv'):
        """
        Parameters:
        -----------
        cards_to_buy: tuple of 2-element tuples
            first element is the card name and second element is the quantity to be bought

        filepath: str
            Default value: 'Data/Yugioh Card Database.csv'

            Filepath that leads to the Yugioh Card Database to initalize a DbHandler Object. Default
            value allows any python file in the same level as the yugioh package to access the database
            directly. A DbHandler Object is required to check the names of cards passed in cards_to_buy

        Variables:
        ----------
        Public:
            driver: webdriver.Chrome() (from Parent Class)
                The driver that opens the Chrome browser from the Selenium Package

            cards_dict: dict
                Dictionary of the name of cards interested in being purchased with their
                quantities

                Keys are name of cards and values are the quantities

        Private:
            card_prices_df: DataFrame() (from Parent Class)
                Dataframe that provides a list of price statistics for specified cards

            combined_df: DataFrame() (from Parent Class)
                Dataframe that merges the card_prices_df and a subset of the yugioh card database
                that includes the columns: Card Type, Competitive Status, and Reference

            normalprice_df: DataFrame()
                Dataframe that contains the Normal price statistics of the cards with their
                purchased quantities

            totalprice_df: DataFrame()
                Dataframe that contains the Total price statistics of the cards with their
                purchased quantities

            cumulative_df: DataFrame()
                Dataframe that contains the summation of Total price statistics of each card,
                multiplied by their purchased quantities

                Represents the total amount of money the user will spend if they decide to go
                through with their choice
        """
        super().__init__(PATH = PATH)
        self.cards_dict = {}
        self.set_buying_dfs(cards_to_buy, filepath)
        self.__normalprice_df = self.get_normalprice_df()
        self.__totalprice_df = self.get_totalprice_df()
        self.__cumulative_df = self.get_cumulative_df()


    def set_buying_dfs(self, cards_to_buy, filepath = 'Data/Yugioh Card Database.csv'):
        """
        Set method that takes in a DbHandler() object from ygfandom module and sets
        multiple dataframes containing the cards to be purchased, their quantities and
        the different types of prices

        Parameters:
        -----------
        cards_to_buy: iterable of 2-element tuples
            first element is the card name and second element is the quantity to be bought

        filepath: str
            Default value: 'Data/Yugioh Card Database.csv'

            Filepath that leads to the Yugioh Card Database. Default value allows any python file in the
            same level as the yugioh package to access the database directly. A DbHanlder object is required
            to cross-reference the cards in the database with their prices
        """
        for cards in cards_to_buy:
            self.cards_dict[cards[0]] = cards[1]
        card_names = self.cards_dict.keys()
        quantities = self.cards_dict.values()

        # Block of code to set the normal_price dataframe, containing the Normal price statistics
        # of the cards with their purchased quantities
        try:
            super().set_card_prices(card_names, filepath)
        except Exception:
            self.__normalprice_df = None
            self.__totalprice_df = None
            self.__cumulative_df = None
            raise Exception('Check the spelling of your card!')
        else:
            self.__normalprice_df = super().get_card_prices()
            if len(self.cards_dict) != 0:
                self.__normalprice_df['Quantity'] = quantities
    
            # Block of code to set the total_price dataframe, containing the Total price statistics
            # of the cards with their purchased quantities
            self.__totalprice_df = self.__normalprice_df.copy()
            for col in self.__totalprice_df.columns:
                if col != 'Quantity':
                    new_col = 'Total' + '(' + col + ')'
                    self.__totalprice_df.rename(columns = {col: new_col}, inplace = True)
                    self.__totalprice_df[new_col] = self.__totalprice_df.apply(lambda x: x[new_col] * x['Quantity'], axis = 1)
    
            # Block of code to set the cummulative dataframe that contains the summation of Total
            # price statistics of each card, multiplied by their purchased quantities. These statistics
            # reflect the total amount of money the user will spend if they decide to go through with
            # their choice
            if len(self.__totalprice_df) != 0:
                self.__cumulative_df = ( self.__totalprice_df.sum()
                                                             .to_frame()
                                                             .rename(columns = {0: 'Cumulative Total'})
                                                             .transpose()
                                                             .rename(columns = {'Quantity': 'Total no. of cards'}) )
                self.__cumulative_df['Total no. of cards'] = self.__cumulative_df['Total no. of cards'].astype('int32')
            else:
                self.__cumulative_df = pd.DataFrame()

    def get_normalprice_df(self):
        """
        Returns the normalprice dataframe which contains the Normal price statistics
        of the cards with their purchased quantities
        """
        return self.__normalprice_df

    def get_totalprice_df(self):
        """
        Returns the totalprice dataframe which contains the Total price statistics
        of the cards with their purchased quantities
        """
        return self.__totalprice_df

    def get_cumulative_df(self):
        """
        Returns the cumulative dataframe which contains the summation of Total price statistics
        of each card, multiplied by their purchased quantities

        These statistics reflect the total amount of money the user will spend if they decide
        to go through with their choice
        """
        return self.__cumulative_df
