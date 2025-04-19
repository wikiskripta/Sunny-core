import sys
import os
sys.path.append(r"/var/www/html/WikiBots/Bot/")
import pywikibot
from pywikibot import pagegenerators
from datetime import datetime, timedelta

os.chdir(os.path.dirname(sys.argv[0]))

task_name = "AISpammerBlocker"
print('Filling queue for ' + task_name + '...')

site = pywikibot.Site()
namespace = 2 # Namespace Uživatel

with open("last_queue_filling_time", "r") as time_file:
    start_time_str = time_file.read().strip()
start_time = datetime.strptime(start_time_str, "%Y-%m-%d %H:%M:%S")
print("Fetching changes since " + start_time_str + ".")

pages = pagegenerators.SubpageFilterGenerator(
    pagegenerators.LogeventsPageGenerator(
        site=site,
        logtype='create',
        namespace=[namespace],
        start=start_time,
        reverse=True
    )
)
page_titles = [page.title() for page in pages]
print("Fetched " + str(len(page_titles)) + " created user pages.")

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

with open("last_queue_filling_time", "w") as time_file:
    time_file.write(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

