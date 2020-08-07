# -*- coding: utf-8 -*-
"""
Created on Thu Aug  6 23:00:39 2020

Author: Jordan Tanudjaja

Script for interacting with the Yugioh Card Database to either update cards,
check the banlist and inspecting any cards that are erroneous in the database
"""

import ygfandom
import concurrent.futures

if __name__ == '__main__':
    
        answer = input("""
        Welcome to Yugioh Card Database (YCD) Interface! What would you like to do today? 
        
        1) Update a few cards in the database using individual card urls
        2) Update cards in the database using new card sets
        3) Checking competitive status of cards in the most recent banlist
        4) Regulatory checkup to see any erroneous or updating 'Not yet released' cards
    
        Choose from option 1 to 4: """)
        
        while True:
            try:
                answer = int(answer)
            except ValueError:
                answer = input("""
        Invalid Answer! Select an option between 1 and 4 to continue: """)
            else:
                if int(answer) not in range(1, 5):
                    answer = input("""
        Invalid Number! Select an option between 1 and 4 to continue: """)
                else:
                    answer = int(answer)
                    break
        
        duelist = ygfandom.DbHandler()
        
        while answer in range(1, 5):
            if answer == 1:
                input_string = input("""
            Insert card URLs separated by a comma: 
            """)
                card_url_list = input_string.replace(' ', '').split(',')
    
                yg_card = ygfandom.WebScraper(card_url_list)
                card_dict_list = yg_card.get_card_details()
    
                for card in card_dict_list:
                    duelist.add_card(card)
    
            elif answer == 2:
                input_string = input("""
            Insert the card set URL:                      
            """)
            
                yg_card_set = ygfandom.WebScraper()
        
                try:
                    yg_card_set.set_card_urls(input_string)
                except:
                    print("""There might be something wrong with the URL or check the method definition,
                          some card sets might not be able to be read by the method and the method definition
                          needs to be changed slightly to accomodate these card sets""")
                else:
                    cards_url_list = yg_card_set.get_card_urls()
        
                with concurrent.futures.ThreadPoolExecutor(max_workers = 5) as executor:
                    executor.map(yg_card_set.set_card_details, cards_url_list)
        
                card_dict_list = yg_card_set.get_card_details()
        
                # Don't use multiprocessing here because the order of saving and adding cards to the database
                # could be messed up
                for card in card_dict_list:
                    duelist.add_card(card)
                    
            elif answer == 3:
                duelist.banlist_update()
            
            elif answer == 4:
                duelist.regulatory_checkup()
                
            answer = input("""
            Would you like to choose anything else? 
            
            1) Update a few cards in the database using individual card urls
            2) Update cards in the database using new card sets
            3) Checking competitive status of cards in the most recent banlist
            4) Regulatory checkup to see any erroneous or updating 'Not yet released' cards
            
            Continue with 1 to 4 or answer anything else besides those numbers to escape: """)
            
            try:
                answer = int(answer)
            except ValueError:
                break
            
        print('Exiting Interface, see you next time!')
            
        
        
    


