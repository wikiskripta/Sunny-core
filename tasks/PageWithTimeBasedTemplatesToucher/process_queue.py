import sys
import os
from datetime import datetime
sys.path.append(r"/var/www/html/WikiBots/Bot/")
import pywikibot

os.chdir(os.path.dirname(sys.argv[0]))

def process_page(title):
    import pywikibot
    site = pywikibot.Site()
    page = pywikibot.Page(site, title)
    page.touch(quiet = True)

task_name = "PageWithTimeBasedTemplatesToucher"
print('Processing queue for ' + task_name + '...')

queue = open('queue', 'r')
processed_pages = 0

page_title = queue.readline()
if (not page_title):
    print('Nothing to process.')
while page_title:
    page_title = page_title.strip()
    print("Processing page " + str(processed_pages + 1) + " – " + page_title, end="... ")
    
    try:
        process_page(page_title)
        print("Page touched.")
    except Exception as e:
        print(str(datetime.now()) + "\t" + "Error while processing page " + page_title + " " + str(e), file=sys.stderr)

    processed_pages += 1
    with open("processed_queue_elements", 'w') as file:
        file.write(str(processed_pages))
    
    page_title = queue.readline()
    
unprocessed_pages = queue.readlines()    
queue.close()

queue = open('queue', 'w')
queue.writelines(unprocessed_pages)
queue.close()

with open("processed_queue_elements", 'w') as file:
    file.write("0")
