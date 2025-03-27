from pywikibot import family

class Family(family.Family):
    name = 'wikiskripta'
    langs = {
        'cs': 'www.wikiskripta.eu',
    }
    
    def scriptpath(self, code):
        return ''
    
    def protocol(self, code):
        return 'HTTPS'
