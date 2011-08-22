import urllib
from StringIO import StringIO
from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName

DEFAULTS = (
    ('Title', '""'),   # academic title
    ('Email', '""'),
    ('First Name', '""'),
    ('Middle Name', '""'),
    ('Last Name', '""'),
    ('Suffix', '""'),
    ('Correspondence Author', 'no'),
    ('Author order Sequence', '""'),
    ('Affiliation order Sequence', '""'),
    ('Author Affiliation', '""'),
    ('Organization Name', '""'),
    ('Department', '""'),
    ('City', '""'),
    ('Zip/Postal Code', '""'),
    ('State/Province', '""'),
    ('Country', '""'),
    ('Abstract Title', '""'),
    ('Abstract', '""'),
    ('Presentation Type', '""'),
    ('Topic', '"4th INCF Congress on Neuroinformatics"'),
    ('Acknowledgements', '""'),
    ('Keywords', '""'),
    ('Conflict of Interest', 'no'),
    )

KEYS = [t[0] for t in DEFAULTS]

TRANSLATIONS = {
    'United Kingdom of Great Britain & Northern Ireland': 'UK',
    'United States of America': 'USA',
    }

def getAdditionalInfo():
    """Extract city and country info from people directory at incf.org"""
    data = urllib.urlopen("http://incf.org/community/people/dumpCityandCountry").read()
    return eval(data)

class Export(BrowserView):
    """Support export to Frontiers in Neuroinformatics"""

    def export2fin(self, delimiter=',', newline='\r\n', testing=None):
        """CSV export using a schema from FIN"""

        out = StringIO()
        out.write(delimiter.join(KEYS) + newline)

        abstracts = self.getAbstracts(testing=testing)
        additional_data = getAdditionalInfo()

        for abstract in abstracts:
            authors = abstract.getAuthors()
            authors = abstract.addAffiliationIndex(authors)
            for index,author in enumerate(authors):
                data = dict(DEFAULTS)
                self.addEntry(data, index, author, abstract, additional_data)
                out.write(delimiter.join([data[k] for k in KEYS]) + newline)

        value = out.getvalue()
        out.close()
        self.request.RESPONSE.setHeader('Content-Type', 'application/x-msexcel')
        self.request.RESPONSE.setHeader("Content-Disposition", 
                                        "inline;filename=INCF2011abstracts.csv")

        return value


    def getAbstracts(self, testing):
        catalog = getToolByName(self.context, 'portal_catalog')
        brains = catalog(portal_type='Abstract',
                         review_state=['accepted', 'published'],
                         )

        # XXX add further logic here if we need to group, sort, or filter
        abstracts = [b.getObject() for b in brains]
        if testing is not None:
            return abstracts[:10]
        else:
            return abstracts

    def addEntry(self, data, index, author, abstract, additional_data):

        author_index = str(index + 1)
        affiliation_index = str(author.get('affiliation_index'))

        data['Email'] = '"%s"' % author.get('email') or ''
        data['First Name'] = '"%s"' % author.get('firstnames') or ''
        data['Last Name'] = '"%s"' % author.get('lastname') or ''
        if index == 0:
            data['Correspondence Author'] = 'yes'
            creator = abstract.Creator()
            city, country = additional_data.get(creator, [None, None])
            if city:
                data['City'] = '"%s"' % city
            if country:
                data['Country'] = '"%s"' % TRANSLATIONS.get(country, country)
        data['Author order Sequence'] = "%s" % author_index
        data['Affiliation order Sequence'] = "%s" % affiliation_index
        data['Author Affiliation'] = "%s*%s" % (author_index, affiliation_index)
        data['Organization Name'] = '"%s"' % author.get('affiliation') or ''
        data['Abstract Title'] = '"%s"' % abstract.Title()
        data['Abstract'] = '"%s"' % abstract.getPlainText(escape_quote=True)
        data['Presentation Type'] = '"%s"' % abstract.getPresentationFormat() or ''
        data['Keywords'] = '"Neuroinformatics, %s"' % abstract.getTopic() or ''



        
