import requests
from bs4 import BeautifulSoup 
import pandas as pd
from datetime import datetime 
import time
import json
from selenium import webdriver 
import re
import random
import os
import saved_keys

# Set Up
main_url = "https://www.xperteleven.com/front_new3.aspx" 
driver = webdriver.Chrome(saved_keys.driver_path)

driver.get(main_url)

# Log in
email = driver.find_element_by_class_name("LogInUserName")
email.send_keys(saved_keys.name)

password = driver.find_element_by_class_name("LogInPassword ")
password.send_keys(saved_keys.password)

login = driver.find_element_by_id("ctl00_cphMain_FrontControl_lwLogin_btnLogin")
login.click()

time.sleep(1)

# Storing team name for later use
team_name = driver.find_element_by_id("ctl00_cphMain_gvFriendsTeam_ctl02_hlFriendTeam").text

# Navigation to the "Matches" screen
driver.find_element_by_id("ctl00_cphMain_gvFriendsTeam_ctl02_hlFriendTeam").click()
driver.find_element_by_id("ctl00_hplTeamMenuLinksMatches").click()

time.sleep(1)

# Archived matches button needs to be clicked to display all matches
driver.find_element_by_id("ctl00_cphMain_chbOld").click()


### Collection of all match URLs by going through all pages of games

# Collecting all links on web page
links = driver.find_elements_by_tag_name('a')

# List for storing URLs
matches = []

# Getting all URLs
for link in links:
    matches.append(link.get_attribute("href"))

# Browing thorugh all pages

clicking = True
while clicking:
    time.sleep(1)
    try:
        driver.find_element_by_link_text("Next").click()
        links = driver.find_elements_by_tag_name('a')
        for link in links:
            matches.append(link.get_attribute("href"))
    except: clicking = False 
    

# Filtering out all links that are not games
match_list = []
for match in matches:
    if "GameID" in str(match):
        match_list.append(match)

print(f"found {len(match_list)} games")

# Lists for storing information about all games to later be visualized
home_away = []
opponents = []
bucs_goals = []
bucs_conceded = []
seasons = []
rounds = []
possession = []
chances = []
motm = []


# Looping through all matches and scarping the desired information
for match in match_list:
    driver.get(match)
    
    # Need to differentiate information depending on home/away team
    if driver.find_element_by_id("ctl00_cphMain_hplHomeTeam").text == team_name:
        
        # Scraping match information
        home_away.append("Home")
        opponents.append(driver.find_element_by_id("ctl00_cphMain_hplAwayTeam").text)
        bucs_goals.append(driver.find_element_by_id("ctl00_cphMain_lblHomeScore").text)
        bucs_conceded.append(driver.find_element_by_id("ctl00_cphMain_lblAwayScore").text)
        possession.append(driver.find_element_by_id("ctl00_cphMain_lblPoss").text)
        chances.append(driver.find_element_by_id("ctl00_cphMain_lblChance").text)
        motm.append(driver.find_element_by_id("ctl00_cphMain_hplBestHome").text)
        
        # html code is slighly different for league games and friendlies
        try:
            seasons.append(driver.find_element_by_id("ctl00_cphMain_lblSeason").text)
            rounds.append(driver.find_element_by_id("ctl00_cphMain_lblOmgang").text)
        except:
            seasons.append("Friendly")
            rounds.append("Friendly")
    else:
        # Scraping match information
        home_away.append("Away")
        opponents.append(driver.find_element_by_id("ctl00_cphMain_hplHomeTeam").text)
        bucs_conceded.append(driver.find_element_by_id("ctl00_cphMain_lblHomeScore").text)
        bucs_goals.append(driver.find_element_by_id("ctl00_cphMain_lblAwayScore").text)
        possession.append(driver.find_element_by_id("ctl00_cphMain_lblPoss").text)
        chances.append(driver.find_element_by_id("ctl00_cphMain_lblChance").text)
        motm.append(driver.find_element_by_id("ctl00_cphMain_hplBestAway").text)
        
        # Differentiate between friendlies and league games
        try:
            seasons.append(driver.find_element_by_id("ctl00_cphMain_lblSeason").text)
            rounds.append(driver.find_element_by_id("ctl00_cphMain_lblOmgang").text)
        except:
            seasons.append("Friendly")
            rounds.append("Friendly")
            
driver.close()


# Calculating points based on goals scored and conceded
points = []

for i in range(0,len(bucs_goals)):
    if bucs_goals[i] > bucs_conceded[i]:
        points.append(3)
    elif bucs_goals[i] < bucs_conceded[i]:
        points.append(0)
    else: points.append(1)
    
    

bucs = ["bucs" for i in range(0,len(match_list))]
df = pd.DataFrame({'Bucs': bucs, 'Goals For': bucs_goals, 'Goals Against': bucs_conceded, 'Points':points,
                   'Opponent': opponents, "Home/Away": home_away, "Season":seasons, "Round":rounds,
                   "Possesion":possession, "Chances":chances, "Man of the Match":motm})

df.to_csv("visualization.csv")