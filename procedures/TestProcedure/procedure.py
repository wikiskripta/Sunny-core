import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-dir", required=True) # PyWikiBot's user-config.py directory
parser.add_argument("--phrase", required=True)
parser.add_argument("--repetition", type=int, required=True)
args = parser.parse_args()

user_config_location = args.dir
phrase = args.phrase
repetition = args.repetition

import sys
import os
sys.path.append(r"/var/www/html/WikiBots/Bot/")
os.chdir(user_config_location)
import pywikibot

site = pywikibot.Site()
page = pywikibot.Page(site, "Uživatel:Sunny/Pískoviště")
page.text = "Sunny's 9th words."
page.save("Automatizovaná editace")

# --------------------------

for _ in range(repetition):
    print(phrase)
