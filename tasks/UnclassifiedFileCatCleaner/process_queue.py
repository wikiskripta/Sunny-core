import sys
import os
from datetime import datetime
sys.path.append(r"/var/www/html/WikiBots/Bot/")
import pywikibot

os.chdir(os.path.dirname(sys.argv[0]))

def process_page(title):
    import pywikibot
    import re
    site = pywikibot.Site()
    page = pywikibot.Page(site, title)

    if not page.exists() or page.isRedirectPage():
        return -1

    categories = [cat.title() for cat in page.categories() if not cat.isHiddenCategory()]

    nonspecific_categories = [
        "Kategorie:Flashové animace",
        "Kategorie:Komprimované archivy",
        "Kategorie:Nezařazené soubory",
        "Kategorie:Obrázky",
        "Kategorie:Videa",
        "Kategorie:Textové soubory",
        "Kategorie:Zvuky",
        "Kategorie:Soubory bez informací o původu",
        "Kategorie:CC-BY soubory",
        "Kategorie:CC-BY-NC soubory",
        "Kategorie:CC-BY-NC-ND soubory",
        "Kategorie:CC-BY-NC-SA soubory",
        "Kategorie:CC-BY-ND soubory",
        "Kategorie:CC-BY-SA soubory",
        "Kategorie:CC0 soubory",
        "Kategorie:GFDL soubory",
        "Kategorie:GPL soubory",
        "Kategorie:LGPL soubory",
        "Kategorie:PD soubory",
        "Kategorie:Soubory bez licence",
        "Kategorie:Soubory s vlastní licencí",
        "Kategorie:Soubory bez uvedeného zdroje",
        "Kategorie:Obrázky s anotacemi",
        "Kategorie:Kategorie:Obrázky s 10+ anotacemi",
        "Kategorie:Obrázky nezobrazené přímo‎"
    ]

    specific_categories = list(set(categories) - set(nonspecific_categories))
    if (len(specific_categories) == 0):
        return 0
    else:
        print("Page is categorized into " + str(len(specific_categories)) + " specific categories: " + str(specific_categories), end=" --> ")
        return 1

def take_action(title):
    import pywikibot
    site = pywikibot.Site()
    page = pywikibot.Page(site, title)
    text = page.text
    new_text = text.replace('[[Kategorie:Nezařazené soubory]]', '')
    page.text = new_text
    page.save("-k Nezařazené soubory || Sunny signs off", quiet = True, tags=["bottask-unclassifiedfilecatclean"])

    
task_name = "UnclassifiedFileCategoryRemover"
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
        page_check_result = process_page(page_title)
        if (page_check_result == 1):
            take_action(page_title)
            print("Page removed from the Unclassified Files category")
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
