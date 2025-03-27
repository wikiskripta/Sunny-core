from pywikibot import family

class Family(family.Family):
    name = 'testwikiskripta'
    langs = {
        'cs': 'tw5.lf1.cuni.cz',
    }
    
    def scriptpath(self, code):
        return ''
    
    def protocol(self, code):
        return 'HTTPS'
