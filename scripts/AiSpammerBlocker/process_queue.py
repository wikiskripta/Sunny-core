import sys
import os
from datetime import datetime
sys.path.append(r"/var/www/html/WikiBots/Bot/")
import pywikibot

os.chdir(os.path.dirname(sys.argv[0]))

def process_page(title):
    import pywikibot
    from pywikibot import data
    import re
    from langdetect import detect
    site = pywikibot.Site()
    page = pywikibot.Page(site, title)
    username = title[(title.index(':')+1):]

    if not page.exists() or page.isRedirectPage():
        return False

    text = page.text
    user = pywikibot.User(site, title)
    spammer_score = -2 # Assume good faith
    
    if (len(text) == 0):
        return spammer_score
    
    # +1 point for each external link, except for the first one
    external_link_pattern = r'https?://(?!wikiskripta\.eu)[^\s]+'
    external_links = re.findall(external_link_pattern, text)
    if (len(external_links) > 1):
        spammer_score += (len(external_links) - 1)
    
    # -4 points for each picture
    image_pattern = r'$$\[File:[^$$]+\]\]|$$\[Soubor:[^$$]+\]\]'
    images = re.findall(image_pattern, text)
    spammer_score -= 4 * len(images)

    # -2 points for each template (mostly stickers)
    template_pattern = r'\{\{[^\}]+\}\}'
    templates = re.findall(template_pattern, text)
    spammer_score -= 2 * len(templates)
    
    # +2 points for page length most common for spammers
    if (len(text) > 320 and len(text) < 650):
        spammer_score += 2

    # +5 points for non-Czech, non-Slovak page
    lang = detect(text)
    if (lang != 'cs' and lang != 'sk'):
        spammer_score += 5
    
    if (spammer_score <= 0):
        return spammer_score; # Spammer score can only decrease from here on
    
    # -1 point for each patrolled or autopatrolled edit out of the latest 50 edits by this user
    response = site.simple_request(action='query',list='usercontribs',ucuser=username,uclimit='50',ucprop='patrolled',format='json').submit()
    user_contribs = response['query']['usercontribs']
    for contrib in user_contribs:
        if 'patrolled' in contrib or 'autopatrolled' in contrib:
            spammer_score -= 1

    # Add more detection filters here if needed
    
    return spammer_score

def take_action(title):
    import pywikibot
    import re
    site = pywikibot.Site()
    page = pywikibot.Page(site, title)
    text = page.text
    user = pywikibot.User(site, title)
    username = title[(title.index(':')+1):]

    # Remove external links from user page
    if (len(text) != 0):
        wiki_link_pattern = r'\[https?:\/\/(?!wikiskripta\.eu)[^\s]+'
        plaintext_link_pattern = r'https?:\/\/(?!wikiskripta\.eu)[^\s]+'
        new_text = re.sub(wiki_link_pattern, '[https://wikiskripta.eu/w/Uživatel:{{subst:PAGENAME}}', text)
        new_text = re.sub(plaintext_link_pattern, 'EXTERNÍ ODKAZ ODSTRANĚN', new_text)
        page.text = new_text
        page.save("Odstranění externích odkazů ze stárnky podezřelého uživatele || Sunny signs off", quiet=True, tags=["bottask-aispammerblock"])
    
    if (not user.is_blocked()):    
        # Add Suspicious User template to user's talk page
        discussion_page = pywikibot.Page(site, "Diskuse s uživatelem:" + username)
        if (discussion_page.text.find('{{Podezřelý účet|') == -1):
            discussion_page.text += "\n{{Podezřelý účet|{{subst:REVISIONTIMESTAMP}}|--~~~~}}"
            discussion_page.save("+š Podezřelý účet || Sunny signs off", quiet=True, tags=["bottask-aispammerblock"])
        
        # Block user from editing main namespace for two weeks
        token = site.simple_request(action='query',meta='tokens',type='csrf').submit()['query']['tokens']['csrftoken']
        req = site.simple_request(action='block',user=username,expiry='2 weeks',nocreate=1,autoblock=1,allowusertalk=1,partial=1,namespacerestrictions="0",token=token,reason="Podezřelý účet: Zablokování editací hlavního jmenného prostoru během dvoutýdenní lhůty pro ověření účtu (viz diskusní stránku uživatele)")
        req.submit()
    
    # Patrol the user page creation edit
    history = list(page.revisions(reverse=True, total=1))
    revid = history[0].revid
    list(site.patrol(revid=revid))

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
        spammer_score = process_page(page_title)
        if (spammer_score > 0):
            take_action(page_title)
            print("Possible spammer detected (score " + str(spammer_score) + ") - External links removed, Suspicious User template added to discussion page and main namespace block created")       
        elif (spammer_score != False):
            print("User unlikely to be a spammer (score " + str(spammer_score) + ")")
        else:
            print("User page was deleted or turned into a redirect")
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

