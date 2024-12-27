from selenium import webdriver
from selenium.webdriver.common.by import By
import pandas as pd
import time

from dateutil import parser
from datetime import datetime


def convert_date(gameDate):
    # Parse the date string (removing the ordinal suffix 'th')
    date_str = gameDate.replace('th', '').replace(
        'nd', '').replace('st', '').replace('rd', '')

    # Parse the date
    parsed_date = parser.parse(date_str)

    # Format the date as "2024-08-12"
    formatted_date = parsed_date.strftime('%Y-%m-%d')

    return formatted_date


def find_first_instance(lst, value):
    try:
        return lst.index(value)
    except ValueError:
        return -1  # Return -1 if the value is not found


# Set up the WebDriver
driver = webdriver.Chrome()


NUM_WEEKS = 17
YEAR = 2024

for week in range(NUM_WEEKS):
    # Navigate to the Next Gen Stats page for that week
    url = f"https://www.nfl.com/schedules/2024/REG{week+1}/"
    driver.get(url)

    # Wait for the page to fully load
    time.sleep(30)
    awayTeams = []
    homeTeams = []
    matchupDates = []

    # First, find the dates each game is played. This will be used to find the weather for that game
    dates = driver.find_elements(By.CLASS_NAME, "d3-l-grid--inner")
    for date in dates:
    
        try:
            # Get the date as a string
            gameDate = date.find_element(By.TAG_NAME, "h2").text
            # And convert it to an easier format to read and use
            gameDate = convert_date(gameDate)
        except:
            # If the date could not be successfully be found or parsed, skip the element
            continue

        # Then, we can find the matchups on that given day
        matchups = date.find_elements(
            By.CLASS_NAME, "nfl-c-matchup-strip")

        for matchup in matchups:
            # Find the teams playing in each matchup
            teams = matchup.find_elements(
                By.CLASS_NAME,  "nfl-c-matchup-strip__team-abbreviation")
            awayTeams.append((teams[0].get_attribute("innerHTML")).strip())
            homeTeams.append((teams[-1].get_attribute("innerHTML")).strip())
            matchupDates.append(gameDate)
    
    # Get the stats for each week as dataframe
    df = pd.read_csv(f"../data/nfl_rushing_stats_week{week+1}.csv")

    # Get the team for each player that week
    teams = df['TEAM']

    opposingTeams = []
    homeGames = []
    gameDates = []

    for team in teams:
        # For each team, we can check if they were the home team that week
        index = find_first_instance(homeTeams, team)
        # If an index found, they are home. Find their opponent and update accordingly
        if (index > 0):
            homeGames.append(True)
            opposingTeams.append(awayTeams[index])

        # If no index found, they are the away team. Update accordingly
        else:
            index = find_first_instance(awayTeams, team)
            try:
                homeGames.append(False)
                opposingTeams.append(homeTeams[index])
            except:
                print(team)
                print(homeTeams)
                print(awayTeams)
        # Add the date for the game as well
        gameDates.append(matchupDates[index])
            

    # Update that weeks stats to include the opposing team, whether it was home or away, and the date they played
    df["OPPOSING_TEAM"] = opposingTeams
    df["HOME"] = homeGames
    df["DATE"] = gameDates

    # Save to CSV or display
    df.to_csv(f"../data/nfl_rushing_stats_week{week+1}.csv", index=False)
    
    print(f"Updated week {week+1}")

# Close the browser
driver.quit()
