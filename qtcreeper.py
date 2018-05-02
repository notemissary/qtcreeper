#!/usr/bin/env python

# qtcreeper.py
# https://github.com/notemissary/qtcreeper
# Based on qtcreeper.py by anonimousse12345, https://github.com/anonimousse12345
# which is based on interpals-autovisit.py by Hexalyse, https://github.com/Hexalyse
# Requires python 3.6 and the requests and ujson module

import ujson
import os
import random
import re
# import shutil
import sys
import time

import requests

# Number of users shown by Interpals per search page
MATCHES_PER_SEARCH = 20

# Masquerade as a random one of these web browsers
# noinspection PyPep8,PyPep8
USER_AGENTS = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_4) " +
    "AppleWebKit/601.5.17 (KHTML, like Gecko) Version/9.1 Safari/601.5.17",
    "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.94 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_4) " +
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.94 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:45.0) Gecko/20100101 Firefox/45.0"
]

CONTINENTS = [
    ("AF", "Africa"),
    ("AS", "Asia"),
    ("EU", "Europe"),
    ("NA", "North America"),
    ("OC", "Oceania"),
    ("SA", "South America")
]

DEFAULT_CONFIG = {
    "continents": [x[0] for x in CONTINENTS],
    "countries": [],
    "keywords": [],
    "age1": 40,
    "age2": 80,
    "sex": ["MALE"],
    "email": "",
    "password": "",
    "creepspeed": 3,
    "maxcreep": 0,
    "useragent": random.choice(USER_AGENTS)
}


DATA_DIR = os.path.join(os.getcwd(), "qtcreeper")
CONFIG_FILE = os.path.join(DATA_DIR, "config.json")
USERS_VISITED_FILE = os.path.join(DATA_DIR, "users_visited.txt")

if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)


def show_exception_and_exit(exc_type, exc_value, tb):
    if exc_type != KeyboardInterrupt:
        print("*** ERROR ***\n")
        import traceback
        traceback.print_exception(exc_type, exc_value, tb)
        input("\nPress enter to exit.")
        sys.exit(-1)


sys.excepthook = show_exception_and_exit


def get_number(prompt_text, default=None):
    print(prompt_text)

    while True:
        i = input("> ")

        try:
            num = int(i)
            return num
        except ValueError:
            pass

        if default is not None and i == "":
            return default
        else:
            print("Invalid selection, try again!")


def get_number_from_list(prompt_text, allowed_options):
    print(prompt_text)

    while True:
        try:
            num = int(input("> "))

            if num in allowed_options:
                return num
        except ValueError:
            pass

        print("Invalid selection, try again!")


def get_iso_codes(prompt_text, allowed_options=None):
    print(prompt_text)

    while True:
        num = input("> ")

        if num == "":
            return []

        iso_codes = [x.strip().upper() for x in num.split(",")]

        fail = False

        # We just check they are two characters
        for isoCode in iso_codes:
            if len(isoCode) != 2 or (allowed_options and isoCode not in allowed_options):
                fail = True
                break

        if not fail:
            return iso_codes

        print("Input invalid, try again!")


def get_word_list(prompt_text):
    print(prompt_text)

    num = input("> ")

    if num == "":
        return []

    words = [x.strip().lower() for x in num.split(",")]
    return [x for x in words if len(x) > 0]


config = {}

print("Welcome to qtcreeper!")
print("--> https://github.com/anonimousse12345/qtcreeper")
print("User settings will be saved in: " + DATA_DIR)

if os.path.exists(CONFIG_FILE):
    with open(CONFIG_FILE, "r") as f:
        config = ujson.loads(f.read())

    # Ensure any later added default keys exist
    for k, v in DEFAULT_CONFIG.items():
        if k not in config:
            config[k] = v
else:
    # Default config
    config = DEFAULT_CONFIG


usersVisited = set()

# Load users already visited
if os.path.exists(USERS_VISITED_FILE):
    with open(USERS_VISITED_FILE, "r") as f:
        for line in f:
            usersVisited.add(line.strip())


while True:
    command = get_number_from_list("\nPlease select an option and press enter:"
                                   + "\n 1 - set username and password ({})".format(config["email"] or "NOT SET!")
                                   + "\n 2 - set gender and age range ({}, {} to {})".format(",".join(config["sex"]),
                                                                                             config["age1"],
                                                                                             config["age2"])
                                   + "\n 3 - set continents ({})".format(",".join(config["continents"]))
                                   + "\n 4 - set countries ({})".format(",".join(config["countries"] or ["All"]))
                                   + "\n 5 - set keywords ({})".format(",".join(config["keywords"] or ["None"]))
                                   + "\n 6 - set creeper speed ({})".format(config["creepspeed"])
                                   + "\n 7 - set maximum qts to creep ({})".format(str(config["maxcreep"] or "")
                                                                                   or "No limit")
                                   + "\n 8 - clear users already visited file ({} users visited)".format(
                                                                                                    len(usersVisited))
                                   + "\n 9 - run creeper!"
                                   + "\n\n 0 - EXIT",
                                   [1, 2, 3, 4, 5, 6, 7, 8, 9, 0])

    if command == 1:
        print("\nEnter username or email address:")
        config["email"] = input("> ").strip().lower()
        print("\nEnter password:")
        config["password"] = input("> ")

    elif command == 2:
        # Get genders
        genders = get_number_from_list("\nWhat genders to crawl? 1 = female, 2 = male, 3 = both", [1, 2, 3])
        config["sex"] = {1: ["FEMALE"], 2: ["MALE"], 3: ["MALE", "FEMALE"]}[genders]

        # Get age range
        config["age1"] = get_number("\nMinimum age?")
        config["age2"] = get_number("\nMaximum age?")

    elif command == 3:
        # Continents
        config["continents"] = get_iso_codes("\nEnter a comma separated list of any of these continent codes, "
                                             "or nothing for all continents:\n"
                                             + "\n".join([(x[0] + " - " + x[1] + " ") for x in CONTINENTS]),
                                             [x[0] for x in CONTINENTS])

        if len(config["continents"]) == 0:
            config["continents"] = [x[0] for x in CONTINENTS]

    elif command == 4:
        # Countries
        config["countries"] = get_iso_codes("\nEnter a comma separated list of two letter country codes, "
                                            "or nothing for all countries:")

    elif command == 5:
        # Keywords
        config["keywords"] = get_word_list("\nEnter a comma separated list of keywords, or nothing to clear:")

    elif command == 6:
        # Set creep speed
        config["creepspeed"] = get_number_from_list("\nEnter a speed between 1 and 10 (1 = slow and realistic, "
                                                    "10 = stupid fast):", range(1, 11))

    elif command == 7:
        # Set max creep
        config["maxcreep"] = get_number("\nEnter the maximum number of qts to creep this run, "
                                        "or nothing for unlimited:", 0)

    elif command == 8:
        # Clear users visited
        if os.path.exists(USERS_VISITED_FILE):
            # # Backup first
            # temp = USERS_VISITED_FILE.replace('\\', '/')
            # shutil.copyfile(temp, temp[:-4] + '_' + time.strftime("%Y-%m-%d_%H:%M:%S")
            #                 + "_BACKUP.txt")
            os.remove(USERS_VISITED_FILE)
        usersVisited = set()

    elif command == 9:
        if config["email"] == "" or config["password"] == "":
            print("\nSet email and password first!")
        else:
            print("\nRunning creeper...")
            break

    elif command == 0:
        exit()

    # Save any changes
    with open(CONFIG_FILE, "w") as f:
        f.write(ujson.dumps(config, indent=4))

    print("\n* Changes saved...")


# File to log users already visited
usersVisitedFp = open(USERS_VISITED_FILE, "a")


def record_user_visited(visited_username):
    visited_username = visited_username.strip()
    usersVisited.add(visited_username)
    usersVisitedFp.write(visited_username + "\n")
    usersVisitedFp.flush()


# Main crawler code below


# Short pause between regular pageloads
def default_wait():
    if config["creepspeed"] < 10:  # don't wait at all at highest speed
        print("\nWaiting...")
        time.sleep(random.uniform(5, 10) / config["creepspeed"])


# Longer(?) pause between user views
def user_view_wait():
    if config["creepspeed"] < 10:  # don't wait at all at highest speed
        sleep_time = random.uniform(5, 15) / config["creepspeed"]
        print("\nWaiting {} seconds...".format(sleep_time))
        time.sleep(sleep_time)


# Start a session
client = requests.Session()
client.headers["Host"] = "www.interpals.net"
client.headers["User-Agent"] = config["useragent"]

print("\nVisiting main page...")

r = client.get("https://www.interpals.net/")
client.headers["Referer"] = "https://www.interpals.net/"

csrf_token = re.findall(r'<meta name="csrf-token" content="([^"]+)"', r.text, re.M)[0]

print("\n* Got CSRF Token: {}".format(csrf_token))

default_wait()

print("\nAttempting login...")

params = {
    "username": config["email"],
    "auto_login": "1",
    "password": config["password"],
    "csrf_token": csrf_token
}

r = client.post("https://www.interpals.net/app/auth/login", data=params)
client.headers["Referer"] = "https://www.interpals.net/account.php"

# print("\n", r.request.headers)

if r.text.find("My Profile") == -1:
    print("\nError: login failed. Either email/password incorrect or qtcreeper needs updating.")

    # with open("debug.txt", "w") as f:
    #    f.write(r.text)

    exit(1)
else:
    print("\n* Successfully logged in!")

default_wait()

print("\nVisiting search page...")
r = client.get("https://www.interpals.net/app/search")
client.headers["Referer"] = "https://www.interpals.net/app/search"

default_wait()


def build_search_url(previous_page_num, desired_page_num):
    # Age
    url = "https://www.interpals.net/app/search?age1={}&age2={}".format(config["age1"], config["age2"])

    # Gender(s)
    for i in range(0, len(config["sex"])):
        url += "&sex[{}]={}".format(i, config["sex"][i])

    # Sorting method
    url += "&sort=last_login"

    # Continents
    for i in range(0, len(config["continents"])):
        url += "&continents[{}]={}".format(i, config["continents"][i])

    # "Looking for"
    url += "&lfor[0]=lfor_email&lfor[1]=lfor_snail&lfor[2]=lfor_langex&lfor[3]=lfor_friend&lfor[4]=lfor_flirt" \
           "&lfor[5]=lfor_relation"

    # First offset, the previous offset/page we were on
    url += "&offset={}".format(previous_page_num * MATCHES_PER_SEARCH)

    # Keywords?
    if len(config["keywords"]) > 0:
        url += "&keywords=" + "+".join(config["keywords"])

    # Online?
    if onlineOnly:
        url += "&online=on"

    # Countries (some strange variable length array)
    url += "&countries[0]=---"

    for i in range(0, len(config["countries"])):
        url += "&countries[{}]={}".format(i+1, config["countries"][i])

    if len(config["countries"]) > 0:
        url += "&countries[{}]=---".format(len(config["countries"])+1)

    # Second offset, the actual offset/page to get
    url += "&offset={}".format(desired_page_num * MATCHES_PER_SEARCH)

    return url


currentSearchPage = 0
onlineOnly = True  # online only by default, but disabled automatically if no users found???
totalViewedCount = 0
totalSkippedCount = 0
ranOutOfUsers = False

while True:
    # Query search page

    userSearchUrl = build_search_url(max(0, currentSearchPage-1), currentSearchPage)
    print("\nQuerying search page {} using search URL: {}".format(currentSearchPage, userSearchUrl))

    r = client.get(userSearchUrl)
    client.headers["Referer"] = userSearchUrl

    # Extract usernames
    usernames = re.findall(r'Report ([a-zA-Z0-9\-_]+) to moderators', r.text, re.M)
    print("\nFound {} users on search page {}.".format(len(usernames), currentSearchPage))

    default_wait()

    # No users were found?
    if len(usernames) == 0:
        print("\n!!!!!!! NO MORE USERS FOUND !!!!!!!")
        print("\nMay have reached end of users. Will now start again including offline users in search.")
        print("\n(Otherwise, try using broader search terms.)")
        currentSearchPage = 0
        onlineOnly = False
        ranOutOfUsers = True
        default_wait()
        continue

    # Through users
    viewedCount = 0
    skippedCount = 0

    for username in usernames:
        if username not in usersVisited:
            print("\nVisiting user {}".format(username))
            client.get("https://www.interpals.net/" + username)

            record_user_visited(username)
            viewedCount += 1
            totalViewedCount += 1

            if totalViewedCount >= config["maxcreep"] > 0:
                break

            user_view_wait()
        else:
            print("\nAlready visited user {}, skipping...".format(username))
            skippedCount += 1
            totalSkippedCount += 1

    print("\n*** RESULTS SO FAR ***\n")
    print(" Search page #{}".format(currentSearchPage))
    print(" Visited {} new users this page, {} were already visited.".format(viewedCount, skippedCount))
    print(" Visited {} new users in total, {} were already visited.".format(totalViewedCount, totalSkippedCount))

    if ranOutOfUsers:
        print("\n!!! WARNING: At one point the script ran out of online users, and started including offline users.")

    if totalViewedCount >= config["maxcreep"] > 0:
        print("\n* Reached qt maximum creep limit {}, shutting down...".format(config["maxcreep"]))
        input("\nPress enter to exit.")
        exit(0)

    # Next page of search
    currentSearchPage += 1
    default_wait()


# Close users visited file??
# usersVisitedFp.close()
