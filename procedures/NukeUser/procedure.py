import argparse

# Setup script parameters
parser = argparse.ArgumentParser()
parser.add_argument("-dir", required=True) # PyWikiBot's user-config.py directory
parser.add_argument("--target_user", required=True)
parser.add_argument("--delete_created_pages", required=True)
parser.add_argument("--revert_user_edits", required=True)
parser.add_argument("--block_user", required=True)
parser.add_argument("--block_reason", required=True)
parser.add_argument("--delete_user", required=True)
args = parser.parse_args()

# Load parameter values
user_config_location = args.dir
target = args.target_user
delete_pages = (args.delete_created_pages == "True")
revert_edits = (args.revert_user_edits == "True")
block_user = (args.block_user == "True")
block_reason = (args.block_reason == "True")
delete_user = (args.delete_user == "True")

# Import PyWikiBot and stuff
import sys
import os
sys.path.append(r"/var/www/html/WikiBots/Bot/")
os.chdir(user_config_location)
import pywikibot
import requests
import re

# TODO - vymaž stránky

# TODO - revertuj editace

# TODO TEST - zablokuj uživatele
token = site.simple_request(action='query',meta='tokens',type='csrf').submit()['query']['tokens']['csrftoken']
req = site.simple_request(action='block',user=target,expiry='never',nocreate=1,noemail=1,allowusertalk=0,token=token,reason=block_reason)
req.submit()

# TODO TEST - odstraň uživatele
wikiApi = "https://www.wikiskripta.eu/api.php"  # TODO support other wiki
wikiWeb = "https://wikiskripta.eu/w/"           # TODO support other wikis
botAccountPassword = "REDACTED"                 # TODO load this from an ENV file or something

# Login and get the session cookie (and user ID/name cookies)
response = requests.post(wikiApi, data={
    "action": "clientlogin",
    "format": "json",
    "loginrequests": "MediaWiki%5CAuth%5CPasswordAuthenticationRequest",
    "loginmessageformat": "raw",
    "loginreturnurl": "https%3A%2F%2Fwikiskripta.eu",
    "logintoken": site.simple_request(action='query',meta='tokens',type='login').submit()['query']['tokens']['logintoken'],
    "username": "Sunny",
    "password": botAccountPassword
})
data = response.json()

if (not data['clientlogin']['status'] == 'PASS'):
    print("ERROR PERFORMING CLIENTLOGIN")
else:
    session = response.cookies.get("wsdb_session")
    userId = response.cookies.get("wsdbUserID")
    userName = response.cookies.get("wsdbUserName")
    
    # Mimic webform request from user merge&delete special page
    url = wikiWeb + "Speci%C3%A1ln%C3%AD:Slou%C4%8Den%C3%AD_u%C5%BEivatel%C5%AF"
    cookies = { # missing wsdbmwuser-sessionId -- is it needed?
        "wsdb_session": session,
        "wsdbUserID": userId,
        "wsdbUserName": userName
    }
    data = {
        "title": "Speciální:Sloučení+uživatelů",
        "wpolduser": target,
        "wpnewuser": "Dummy",
        "wpdelete": 1,
        "wpEditToken": site.simple_request(action='query',meta='tokens',type='csrf').submit()['query']['tokens']['csrftoken']
    }
    
    response = requests.post(url, cookies=cookies, data=data)
    
    # Check that response contains deletion successful message"
    if re.search(f"Účet {target} \(\d+\) byl smazán\.", response):
        print("Target account was successfully deleted.")
    else:
        print("Unexpected response for the account merge&delete request: " + response)
