from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException
import time 
from time import sleep
import pandas as pd

OPERATOR = '10CRIC'

driver = webdriver.Chrome()
driver.maximize_window()
driver.get("https://www.10crickbet.com/casino/")
sleep(5)

# Set a scroll height to track progress
last_height = driver.execute_script("return document.body.scrollHeight")
inner_height = driver.execute_script("return window.innerHeight")
print('last height: ', last_height)
print('inner height: ', inner_height)

new_height = inner_height

while True:
    driver.execute_script("window.scrollTo(0, {});".format(new_height))
    sleep(5)

    # Check if new content has been loaded
    new_last_height = driver.execute_script("return document.body.scrollHeight")
    if new_last_height == last_height:
        print("No new content loaded. Exiting loop.")
        break

    # Update last height and scroll position
    last_height = new_last_height
    new_height += inner_height
    print('New height: ', new_height)

print("Reached the end of scrollable content.")

# Scroll back to the top
driver.execute_script("window.scrollTo(0, 0);")
time.sleep(2)

try:
    main_container = driver.find_element(By.CLASS_NAME, "dn-slide-body")
    no_thanks_button = main_container.find_element(By.CLASS_NAME, "dn-slide-deny-btn")
    no_thanks_button.click()
    print("Clicked 'No Thanks' button successfully")
    sleep(3)
except NoSuchElementException:
    print("No Thanks button or main container not found")

# Do something with the scraped content (replace with your logic)
game_collections = driver.find_elements(By.CLASS_NAME, "CategoryGames_container__Kzicl")

all_df = pd.DataFrame()
game_collection_cnt = 1
for game_collection in game_collections:
    game_collection_title = game_collection.find_element(By.CLASS_NAME, "CategoryHeader_title__URUcM").text
    game_collection_title = game_collection_title.split('(')[0]
    print(game_collection_title)
    game_titles = game_collection.find_elements(By.CLASS_NAME, "GameCard_title__5LZ_f")
    game_providers = game_collection.find_elements(By.CLASS_NAME, "GameCard_subTitle__l52e0")
    game_images = game_collection.find_elements(By.CLASS_NAME, "GameCard_image__KBnCK")

    # Extract and print the text from each element
    print(len(game_titles), len(game_providers), len(game_images))

    game_names = []
    game_provider_names = []
    game_image_links = []
    game_positions = []
    game_positions_x = []
    game_positions_y = []

    for i in range(len(game_titles)):
        y_coordinate = driver.execute_script("return arguments[0].getBoundingClientRect().top + window.pageYOffset;", game_titles[i]) - 100
        driver.execute_script("window.scrollTo(0, {});".format(y_coordinate))
        sleep(0.5)
        hover = ActionChains(driver).move_to_element(game_titles[i])
        hover.perform()
        sleep(0.5)

        section_scroll_counter = 1
        while True:
            try:
                driver.get_screenshot_as_file('./{0}_{1}_{2}.png'.format(OPERATOR, game_collection_title, section_scroll_counter))
                section_scroll_counter += 1
            except:
                break

        game_names.append(game_titles[i].text)
        game_provider_names.append(game_titles[i].text)
        game_image_links.append(game_images[i].get_attribute("src"))
        game_positions.append(i+1)
        game_positions_x.append(game_titles[i].location['x'])
        game_positions_y.append(game_titles[i].location['y'])

    df = pd.DataFrame()
    df['game_name'] = pd.Series(game_names)
    df['game_provider_name'] = pd.Series(game_provider_names)
    df['game_image_link'] = pd.Series(game_image_links)
    df['game_position'] = pd.Series(game_positions)
    df['operator'] = OPERATOR
    df['game_collection_title'] = game_collection_title
    df['game_collection_cnt'] = game_collection_cnt
    df['game_pos_x'] = pd.Series(game_positions_x)
    df['game_pos_y'] = pd.Series(game_positions_y)

    df = df[df['game_name'] != '']
    print(len(df))

    if len(all_df) == 0:
        all_df = df.copy()
    else:
        all_df = pd.concat([all_df, df], axis=0)

    game_collection_cnt += 1

csv_file_path = r"C:\Vindiata\AWS Repositories\game_observer\Parser\scraper_data\{}.csv".format(OPERATOR)
all_df.to_csv(csv_file_path, index=False)

driver.quit()
