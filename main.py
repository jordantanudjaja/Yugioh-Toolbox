# -*- coding: utf-8 -*-
"""
Created on Thu Aug 6 23:00:39 2020

Author: Jordan Tanudjaja

Script for interacting with the Yugioh Card Database to either update cards,
check the banlist, or inspect any cards that are erroneous in the database
"""

from yugioh import ygfandom as ygf
from yugioh import banlist
from yugioh import tcgplayer as tcg
import time

if __name__ == '__main__':

        NUM_OPTIONS = 7

        OPTIONS = """
        1) Update a few cards in the database using individual card urls
        2) Update cards in the database using new card sets
        3) Check competitive status of cards in the most recent banlist
        4) Regulatory checkup to see any erroneous or updating 'Not yet released' cards
        5) Check current prices of any yugioh card (even those not in the Yugioh Card Database)
        6) Check the current prices of a card/cards that are only in the current Yugioh Card Database
        7) Plan shopping cart for purchasing cards in the current Yugioh Card Database
        """

        answer = input(f"""
        Welcome to Yugioh Card Database (YCD) Interface! What would you like to do today?

        {OPTIONS}

        Choose from option 1 to {NUM_OPTIONS}: """)

        while True: # Do-while loop to make sure the user enters in the correct option
            try:
                answer = int(answer)
            except ValueError:
                answer = input(f"""
        Invalid Answer! Select an option between 1 and {NUM_OPTIONS} to continue: """)
            else:
                if int(answer) not in range(1, NUM_OPTIONS + 1):
                    answer = input(f"""
        Invalid Number! Select an option between 1 and {NUM_OPTIONS} to continue: """)
                else:
                    answer = int(answer)
                    break

        duelist = ygf.DbHandler() # Instantiating a DbHandler() object to reference the Yugioh Card Database

        while answer in range(1, NUM_OPTIONS + 1):
            if answer == 1:
                input_string = input("""
            Insert card URLs separated by a SPACE:
            """)
                card_url_list = input_string.split(' ')

                yg_card = ygf.YgScraper() # Instantiating a YgScraper() object to scrape the site for card setails
                yg_card.add_card_urls(card_url_list)
                card_dict_list = yg_card.get_card_details()

                for card in card_dict_list:
                    duelist.add_card(card)

            elif answer == 2:
                input_string = input("""
            Insert the card set URL:
            """)

                yg_card_set = ygf.YgScraper() # Instantiating a YgScraper() object to scrape the site for card urls
                                              # and card details

                try:
                    yg_card_set.set_card_urls(input_string)
                except:
                    print("""There might be something wrong with the URL or check the method definition,
                          some card sets might not be able to be read by the method and the method definition
                          needs to be changed slightly to accomodate these card sets""")

                card_dict_list = yg_card_set.get_card_details()

                # Don't use multiprocessing here because the order of saving and adding cards to the database
                # could be messed up
                for card in card_dict_list:
                    duelist.add_card(card)

            elif answer == 3:
                updated_df = banlist.banlist_update(duelist)

            elif answer == 4:
                updates_needed_df = duelist.regulatory_checkup()
                print(updates_needed_df)
                print('Use Jupyter Notebook to better visualize the properties of cards that needs to be updated')

            elif answer == 5:
                input_string = input(f"""
            Insert the name of the card you would like to search (ONLY 1 CARD AT A TIME):
            """)
                card_search = tcg.CardPriceScraper() # Instantiating a CardPriceScraper() object to scrape the site
                                                     # for prices of the card that was inputted

                price_stats = card_search.price_searcher(input_string)
                print(price_stats)
                time.sleep(2) # Delaying 2 seconds before closing the browswer
                card_search.quit_browser()

            elif answer == 6:
                card_names_list = []
                input_string = input(f"""
                Insert a card name (ONLY 1 AT A TIME):
                """)

                while True: # Do-while loop to get all the cards the user inputted until he/she is satisfied
                    tosearch_df = duelist.search_card_name(input_string)
                    if len(tosearch_df) != 0:
                        card_names_list.append(input_string)
                        print('Card succesfully found in the database')
                    else:
                        pass
                    input_string = input(f"""
                    Insert another card name or type 'esc' to escape:
                    """)
                    if input_string == 'esc':
                        break

                card_bundle = tcg.CardPriceScraper() # Instantiating a CardPriceScraper() object to scrape the site
                                                     # for prices of cards in the card bundle
                card_bundle.set_card_prices(card_names_list, duelist)
                card_prices = card_bundle.get_card_prices()
                print(card_prices)
                time.sleep(2) # Delaying 2 seconds before closing the browser
                card_bundle.quit_browser()

            elif answer == 7:
                cards_to_buy = []
                input_string = input(f"""
                Insert a card name (ONLY 1 AT A TIME):
                """)

                while True: # Do-while loop to get all the cards and the quantities of each card the user wants to purchase
                             # until he/she is satisfied
                    tosearch_df = duelist.search_card_name(input_string)
                    if len(tosearch_df) != 0:
                        print('Card succesfully found in the database')

                        while True:
                            input_quantity = input(f""""
                            Input the number of {input_string} cards you want to buy:
                            """)
                            try:
                                input_quantity = int(input_quantity)
                            except:
                                print('That is not an integer, input an integer value!')
                            else:
                                cards_to_buy.append((input_string, input_quantity))
                                break
                    else:
                        pass
                    input_string = input(f"""
                    Insert another card name or type 'esc' to escape:
                    """)
                    if input_string == 'esc':
                        break

                shopping_cart = tcg.BuyingTool(cards_to_buy, duelist)
                normalprices_df = shopping_cart.get_normalprice_df()
                totalprices_df = shopping_cart.get_totalprice_df()
                cumulative_df = shopping_cart.get_cumulative_df()

                print(f"""
                Base Prices of cards (Qty: 1)
                {normalprices_df}
                """)

                print(f"""
                Total Prices of cards (Price x Qty)
                {totalprices_df}
                """)

                print(f"""
                Potential Total Money spent
                {cumulative_df}
                """)

                time.sleep(2) # Delay 2 seconds before closing browser
                shopping_cart.quit_browser()

            answer = input(f"""
            Would you like to choose anything else?

            {OPTIONS}

            Continue with 1 to {NUM_OPTIONS} or answer anything else besides those numbers to escape: """)

            try:
                answer = int(answer)
            except ValueError:
                break

        print('Exiting Interface, see you next time!')
