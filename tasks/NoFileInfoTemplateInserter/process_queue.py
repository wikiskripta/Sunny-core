import sys
import os
from datetime import datetime
sys.path.append(r"/var/www/html/WikiBots/Bot/")
import pywikibot

os.chdir(os.path.dirname(sys.argv[0]))

def process_page(title):
    site = pywikibot.Site()
    page = pywikibot.Page(site, title)

    if not page.exists() or page.isRedirectPage():
        return -1

    text = page.text
    
    if (text.find("{{Soubor") != -1):
        # Odchytí i {{Soubor bez informací}}
        return 0
    elif (text.find("#PŘESMĚRUJ") != -1):
        return -1
    else:
        return 1

def take_action(title):
    site = pywikibot.Site()
    page = pywikibot.Page(site, title)
    new_text = page.text + "\n\n{{Soubor bez informací}}"
    page.text = new_text
    page.save("+š Soubor bez informací || Sunny signs off", quiet = True, tags=["bottask-nofileinfotemplateinsert"])


task_name = "NoFileInfoTemplateInserter"
print('Processing queue for ' + task_name + '...')

queue = open('queue', 'r')
processed_pages = 0

page_title = queue.readline()
if (not page_title):
    print('Nothing to process.')
while page_title:
    page_title = page_title.strip()
    print("Processing page " + str(processed_pages + 1) + " – " + page_title, end="... ")

    edit_made = False
    try:
        page_check_result = process_page(page_title)
        if (page_check_result == 1):
            take_action(page_title)
            print("Page updated")
        elif (page_check_result == 0):
            print("Page left intact")
        else:
            print("Page was deleted or turned into a redirect")
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
