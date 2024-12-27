from selenium import webdriver
from selenium.webdriver.common.by import By
import pandas as pd
import time

# What to do:
# Scrape the data for each week, save each one as separate csv

# For each folder, get a list of schedules for that week
# Loop through each player, map their team to their opponent
# Use the opponent location to find the weather on that day at that time in that location
# Cache this result so you only need to do it once per team that week
# Append the data to the player stats for that week (ie temp, wind, humidity, etc)

# Append all weeks together for a massive list of all performances this year

# BONUS STEP:
# Add opponent defense ratings so there is a discrete ranking for oppenents, not just the team itself

# LAST STEP:
# Scrape bet books to find any over unders that are udnervalued

# BONUS LAST STEP:
# Rake in the dough
# Upload dataset to kaggle


driver = webdriver.Chrome()


NUM_WEEKS = 17

for week in range(NUM_WEEKS):
    # Navigate to the Next Gen Stats page for that week
    url = f"https://nextgenstats.nfl.com/stats/rushing/2024/REG/{week+1}#yards"
    driver.get(url)

    # Wait for the page to fully load
    time.sleep(10)

    # Locate the stats table headers
    headerTable = driver.find_element(By.CLASS_NAME, "el-table__header")

    # Locate the stats table
    statTable = driver.find_element(By.CLASS_NAME, "el-table__body")

    # Extract table headers
    headers = [header.text for header in headerTable.find_elements(
        By.TAG_NAME, "th")]

    # # Extract table rows
    rows = []
    for row in statTable.find_elements(By.TAG_NAME, "tr"):
        cols = [col.text for col in row.find_elements(By.TAG_NAME, "td")]
        if cols:  # Skip empty rows
            rows.append(cols)

    # Convert the data to a DataFrame
    df = pd.DataFrame(rows, columns=headers)

    # Remove empty first column (would refer to player names)
    # NOTE: The way the data is displayed, the player names are all empty strings
    del df[df.columns[0]]

    # Save to CSV or display
    df.to_csv(f"../data/nfl_rushing_stats_week{week+1}.csv", index=False)

# Close the browser
driver.quit()
