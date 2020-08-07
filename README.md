# Yugioh-Python-Package
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
    <li><b>ygfandom:</b> Module containing classes to view and make changes to the Yugioh Card Database.csv file
    through web scraping the website: https://yugioh.fandom.com</li>
</ul>

<h3>Jupyter Notebooks</h3>
<ul>
    <li><b>Analytics and Checkup:</b> Notebook platform for doing quality checkup on the card database and doing any type of
    data analysis, visualization and editing or updating card data</li>
    <li><b>Card Database Initialization:</b> First notebook created to initialize the Yugioh Card Database.csv file. It contains
    functions that was used to scrape the https://yugioh.fandom.com for card sets (packs, decks, collectible tins etc) urls
    and grab each card's information and store it in a DataFrame format </li>
</ul>

<h3>Main Python file</h3>
Python Script that provides the user with an interface to interact with the Yugioh Card Database. It has 4 functions:
<ol>
    <li>Updating new cards to the database individually or in small amounts using their own unique URL</li>
    <li>Updating new cards to the database through a card set URL, such as booster pack or structure decks</li>
    <li>Updating the competitive status of the cards through cross-referencing with the current banlist</li>
    <li>Doing a regulatory checkup and seeing if there is any errors in adding new cards or if
    there is a need to update status of existing cards </li>
</ol>
