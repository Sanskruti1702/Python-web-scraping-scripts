import sys
from pathlib import Path
sys.path.extend([str(Path(__file__).resolve().parent.parent)])

import pandas as pd
from sqlalchemy import create_engine
from connectors import data_write_engine, data_fetcher
from auxiliary.scraper_list import scraper_dict
from selenium import webdriver
from selenium.webdriver.common.by import By
import time

# fetch games
# games_df = data_fetcher("""
#     select distinct name as game_name
#     from igamingcompass.game_aliases
# """, ['game_name'])
# games_df['game_name'] = games_df['game_name'].astype('str')

# games_df.to_csv('games_list.csv', index=False)

games_df = pd.read_csv('games_list.csv')
print(games_df.head())
print(games_df.shape)


all_data = []
for i in range(len(games_df)):
    row = games_df.iloc[i]
    game_name = row['game_name']

    dicty = {
        'game_name': game_name,
        'slotcatalog': None,
        'casino_guru': None
    }

    driver = webdriver.Chrome()
    driver.set_window_size(1920, 1080)
    
    # SLOTCATALOG CHECK
    driver.get("https://slotcatalog.com/en")
    time.sleep(3)
    name_input = driver.find_element(By.ID, 'selsearch')
    name_input.send_keys(game_name)
    time.sleep(2)
    try:
        search_menu = driver.find_element(By.CLASS_NAME, 'tt-dataset')
        search_result = search_menu.find_element(By.CLASS_NAME, 'tt-suggestion')
        dicty['slotcatalog'] = search_result.get_attribute('href')
    except:
        pass

    # CASINO GURU CHECK
    driver.get("https://casino.guru/free-casino-games")
    time.sleep(3)
    name_input = driver.find_element(By.CLASS_NAME, 'header-search-input')
    name_input.send_keys(game_name)
    time.sleep(2)
    try:
        search_menu = driver.find_element(By.CLASS_NAME, 'search-box-results')
        search_result_groups = search_menu.find_elements(By.CLASS_NAME, 'js-search-results-group')
        for group in search_result_groups:
            header = group.find_element(By.CLASS_NAME, 'search-results-group-header')
            if header.text == 'Games':
                group_item = group.find_element(By.CLASS_NAME, 'js-search-results-group-item')
                dicty['casino_guru'] = group_item.get_attribute('href')
                break
    except:
        pass
    
    driver.quit()

    all_data.append(dicty)
    if i==5:
        break

all_df = pd.DataFrame(all_data)
all_df.to_csv('games_master.csv', index=False)