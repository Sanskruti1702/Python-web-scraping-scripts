from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import Select
from time import sleep
import datetime
import pandas as pd

driver = webdriver.Chrome()
driver.set_window_size(1440, 1080)
driver.get("https://climate.weather.gc.ca/climate_data/daily_data_e.html?StationID=47707")
sleep(5)
current_month = datetime.datetime.now().month
current_year = datetime.datetime.now().year

col_names = driver.find_element(By.TAG_NAME, 'thead').find_elements(By.TAG_NAME, 'th')

keys=[]
for col in col_names:
    header_text = col.find_element(By.TAG_NAME, 'a').text if col.find_elements(By.TAG_NAME, 'a') else col.text.strip()
    if '\n' in header_text:
        header_text = header_text.split('\n')[0]
    keys.append(header_text)
# print(keys)
final_df = pd.DataFrame(columns=keys + ['Month', 'Year'])
    
for month in range(1, current_month + 1):
    select_month = Select(driver.find_element(By.ID, "Month1"))
    select_month.select_by_value(str(month))

    select_year = Select(driver.find_element(By.ID, "Year1"))
    select_year.select_by_value(str(current_year))

    # Click the "Go" button
    go_button = driver.find_element(By.CSS_SELECTOR, "#Month1 + input[type='submit']")
    go_button.click()

    sleep(5)
    
    # Finding the Year and Month Name from the url page
    year_element = driver.find_element(By.CSS_SELECTOR, "#Year1 option[selected='selected']")
    month_element = driver.find_element(By.CSS_SELECTOR, "#Month1 option[selected='selected']")

    year_value = year_element.get_attribute("value")
    month_value = month_element.text

    # Print the year and month values
    # print("Year:", year_value)
    # print("Month:", month_value)
    
    last_height = driver.execute_script("return document.body.scrollHeight")
    inner_height = driver.execute_script("return window.innerHeight")

    new_height = inner_height

    while True:
        driver.execute_script("window.scrollTo(0, {});".format(new_height))
        sleep(2)
        new_height += inner_height
        # print('New height: ', new_height)
        last_height = driver.execute_script("return document.body.scrollHeight")
        if new_height >= last_height:
        # print("Reached the end of scrollable content.")
            break

    
    # Finding the row data from the url page
    rows = driver.find_elements(By.XPATH, "//tbody/tr")
    data = []
    for row in rows[:-4]:
        cells = row.find_elements(By.XPATH, ".//th | .//td")
        row_data = []
        for cell in cells:
            cell_text = ' '.join([text for text in cell.text.split() if not text.startswith('Legend')])
            row_data.append(cell_text.strip())
        data.append(row_data)
        print(row_data)
        
df = pd.DataFrame(data, columns=keys)
df['Month'] = month_value
df['Year'] = year_value
final_df = pd.concat([final_df, df], ignore_index=True)
#     print(data)
print(final_df)
driver.quit()
