# Yugioh Web-Scraping Toolbox
Anything related to Yugioh (Card Database, Updating new cards, Banlist, Card Prices) are all here

<h2>yugioh Package</h2>
<h3>Data</h3>
<ul>
    <li><b>Yugioh Card Database.csv:</b> CSV file that contains 99% of Yugioh cards up to the current Link format</li>
    <li><b>Yugioh Card Database (Backup).csv:</b> Same csv file as Yugioh Card Database.csv that serves as a backup
    file in case something happens to the original file</li>
</ul>

<h3>Modules</h3>
<ul>
    <li><b>__init__:</b> Initialization Module</li>
    <li><b>ygfandom:</b> Module containing classes to view and make changes to the Yugioh Card Database.csv or the
    backup csv file through web scraping the website: https://yugioh.fandom.com</li>
    <li><b>banlist:</b> Module containing the banlist_update function that scrapes the website:
    https://www.yugioh-card.com/uk/gameplay/detail.php?id=1155 and updates the card database according to the most
    recent banlist</li>
    <li><b>tcgplayer:</b> Module containing classes that scrapes the website: https://www.tcgplayer.com and searches
    the current card prices of cards the user is interested in buying and returns pre-defined price statistics</li>
</ul>

<h2>Jupyter Notebooks</h2>
<ul>
    <li><b>Analytics and Checkup:</b> Notebook platform for doing quality checkup on the card database and doing any type of
    data analysis, visualization and editing or updating card data</li>
    <li><b>Card Database Initialization:</b> First notebook created to initialize the Yugioh Card Database.csv file. It contains
    functions that were used to scrape the https://yugioh.fandom.com for card sets (packs, decks, collectible tins etc) urls
    and grab each card's information and store it in a DataFrame format</li>
    <li><b>Card Price Toolbox:</b> Notebook platform to analyze and compare different card prices and provide a shopping cart
    for users to make purchasing decisions. Potential expansion includes a deck building toolbox embedded in this notebook</li>
</ul>

<h2>Main Python file</h2>
Python Script that provides the user with an interface to interact with the Yugioh Card Database. It has 7 functions:
<ol>
    <li>Updating new cards to the database individually or in small amounts using their own unique URL</li>
    <li>Updating new cards to the database through a card set URL, such as booster pack or structure decks</li>
    <li>Updating the competitive status of the cards through cross-referencing with the current banlist</li>
    <li>Doing a regulatory checkup and seeing if there is any errors in adding new cards or if
    there is a need to update status of existing cards </li>
    <li>Checking current prices of any Yugioh card (even those not in the Yugioh Card Database)</li>
    <li>Checking the current prices of a card/cards that are only in the current Yugioh Card Database</li>
    <li>Planning a shopping cart for purchasing cards in the current Yugioh Card Database</li>
</ol>
