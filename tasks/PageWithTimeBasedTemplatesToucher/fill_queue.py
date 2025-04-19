import sys
import os
sys.path.append(r"/var/www/html/WikiBots/Bot/")
import pywikibot
from pywikibot import pagegenerators
from datetime import datetime, timedelta

os.chdir(os.path.dirname(sys.argv[0]))

task_name = "PageWithTimeBasedTemplatesToucher"
print('Filling queue for ' + task_name + '...')

site = pywikibot.Site()

pages = pagegenerators.CategorizedPageGenerator(
    category=pywikibot.Category(site, "Stránky s časově závislými šablonami")
)

page_titles = []
for page in pages:
    page_titles.append(page.title())
print("Fetched " + str(len(page_titles)) + " pages from the Pages with time-based templates category")

with open("queue", "r") as file:
    queue = [line.strip() for line in file.readlines()]

with open("processed_queue_elements", "r") as count_file:
    finished_count = int(count_file.read().strip())

queue = queue[finished_count:]
print("Combining with " + str(len(queue)) + " pages left in the queue and removing duplicates.")

combined = list(dict.fromkeys(queue + page_titles))
print("Resulting queue contains " + str(len(combined)) + " pages.")

with open("queue", "w") as file:
    for line in combined:
        file.write(line + "\n")

with open("processed_queue_elements", "w") as count_file:
    count_file.write("0")

