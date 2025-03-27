import sys
import os
from datetime import datetime
sys.path.append(r"/var/www/html/WikiBots/Bot/")
import pywikibot

os.chdir(os.path.dirname(sys.argv[0]))

def process_page(title):
    site = pywikibot.Site()
    page = pywikibot.Page(site, title)
    username = title[(title.index(':')+1):]
    user = pywikibot.User(site, username)
    if (user.is_blocked()):
        return 0 # Již zablokovaný uživatel
    elif (len(set(user.groups()) - set(['*', 'user'])) > 0):
        return -1 # Uživatel s manuálně přidělenou rolí, pravděpodobně člen WikiTýmu nebo učitel, takoví by neměli být blokování automaticky
    elif ('/' in title):
        return -2 # Podstránka (pravděpodobně pískoviště nějakého uživatele)
    else:
        return 1

def take_action(title, block = False):
    from pywikibot import data
    import re
    from langdetect import detect
    site = pywikibot.Site()
    page = pywikibot.Page(site, title)
    username = title[(title.index(':')+1):]
    text = page.text
    
    if (block):
        # Načíst stránku, která je v kategorii
        # Zjistit, co je na ní za šablonu:
        #   Podezřelý účet? ==> reason="Podezřelý účet"
        #   Zablokovat? ==> reason=načtený první parametr (důvod)
        m = re.search(r".*\{\{\s*(Zablokovat|Podezřelý účet)\s*\|(.*)\}\}.*", text)
        if (m is not None):
            if (m.group(1) == 'Podezřelý účet'):
                reason = "Podezřelý účet"
            else:
                reason = m.group(2)
        else:
            reason = "Zablokování na základě přímé kategorizace do Kategorie:Zablokovat"

        # Zablokuj trvale uživatele na celém projektu, povol mu editaci vlastní uživatelské diskuse
        token = site.simple_request(action='query',meta='tokens',type='csrf').submit()['query']['tokens']['csrftoken']
        req = site.simple_request(action='block',user=username,expiry='never',nocreate=1,noemail=1,allowusertalk=1,token=token,reason=reason)
        req.submit()
    
    # Dekategorizuj uživatelskou stránku
    text = text.replace('[[Kategorie:Zablokovat]]', '') # Přímá kategorizace
    text = re.sub(r'\{\{\s*Zablokovat\s*\|(.*?)\}\}', lambda m: '{{Zablokovat|' + m.group(1).replace('|', '{{!}}') + '|hotovo=ano}}', text) # Šablona Zablokovat
    text = re.sub(r'\{\{\s*Podezřelý účet\s*\|\s*\d*\s*\|(.*)\}\}', lambda m: '{{Podezřelý účet|0|' + m.group(1).replace('|', '{{!}}') + '}}', text) # Šablona Podezřelý účet
    page.text = text
    page.save("Odebrání kategorizace do Kategorie:Zablokovat po zablokování uživatele || Sunny signs off", quiet = True, tags=["bottask-blockcatclean"])

task_name = "AISpammerBlocker"
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
        to_be_blocked = process_page(page_title)
        if (to_be_blocked == 1):
            take_action(page_title, True)
            print("Unblocked user in the Block category found, blocking and removing from the category.")       
        elif (to_be_blocked == 0):
            print("Blocked user in the Block category found, removing from the category.")
            take_action(page_title)
        else:
            print("User is a WikiTeam member and cannot be blocked automatically or the page is not a root user page or root user discussion page.")
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
