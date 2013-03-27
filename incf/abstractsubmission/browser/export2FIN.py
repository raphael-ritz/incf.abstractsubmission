from StringIO import StringIO
from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName

DEFAULTS = (
    ('Userid', '""'),
    ('Review State', '""'),
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
    ('Topic', '""'),
    ('Acknowledgements', '""'),
    ('References', '""'),
    ('Keywords', '""'),
    ('Conflict of Interest', 'no'),
    )

KEYS = [t[0] for t in DEFAULTS]

TRANSLATIONS = {
    'United Kingdom of Great Britain & Northern Ireland': 'UK',
    'United States of America': 'USA',
    }


class Export(BrowserView):
    """Support export to Frontiers in Neuroinformatics"""

    def export2fin(self, delimiter=',', newline='\r\n', testing=None, ALL=False):
        """CSV export using a schema inspired by FIN
        If 'testing' is not None at most 10 abstracts are returned.
        If ALL is true abstracts in all review states are included"""

        out = StringIO()
        out.write(delimiter.join(KEYS) + newline)

        abstracts = self.getAbstracts(testing=testing, ALL=ALL)

        for abstract in abstracts:
            authors = abstract.getAuthors()
            authors = abstract.addAffiliationIndex(authors)
            for index,author in enumerate(authors):
                data = dict(DEFAULTS)
                self.addEntry(data, index, author, abstract)
                out.write(delimiter.join([data[k] for k in KEYS]) + newline)

        value = out.getvalue()
        out.close()
        self.request.RESPONSE.setHeader('Content-Type', 'application/x-msexcel')
        self.request.RESPONSE.setHeader("Content-Disposition", 
                                        "inline;filename=abstracts.csv")

        return value


    def getAbstracts(self, testing, ALL):
        catalog = getToolByName(self.context, 'portal_catalog')
        if ALL:
            brains = catalog(portal_type='Abstract')
        else:
            brains = catalog(portal_type='Abstract',
                         review_state=['accepted', 'published'],
                         )

        # XXX add further logic here if we need to group, sort, or filter
        abstracts = [b.getObject() for b in brains]
        if testing is not None:
            return abstracts[:10]
        else:
            return abstracts

    def addEntry(self, data, index, author, abstract):

        author_index = str(index + 1)
        affiliation_index = str(author.get('affiliation_index'))

        data['Userid'] = '"%s"' % abstract.Creator() or ''
        data['Review State'] =  '"%s"' % abstract.portal_workflow.getInfoFor(abstract, 'review_state')
        data['Email'] = '"%s"' % author.get('email') or ''
        data['First Name'] = '"%s"' % author.get('firstnames') or ''
        data['Last Name'] = '"%s"' % author.get('lastname') or ''
        if index == 0:
            data['Correspondence Author'] = 'yes'
        country = author.get('country')
        if country:
            data['Country'] = '"%s"' % TRANSLATIONS.get(country, country)
        data['Author order Sequence'] = "%s" % author_index
        data['Affiliation order Sequence'] = "%s" % affiliation_index
        data['Author Affiliation'] = "%s*%s" % (author_index, affiliation_index)
        data['Organization Name'] = '"%s"' % author.get('affiliation') or ''
        data['Abstract Title'] = '"%s"' % abstract.Title()
        data['Abstract'] = '"%s"' % abstract.getPlainText(escape_quote=True)
        data['Acknowledgements'] = '"%s"' % abstract.getAcknowledgments() or ''
        data['References'] = '"%s"' % abstract.getCitations() or ''
        data['Presentation Type'] = '"%s"' % abstract.getPresentationFormat() or ''
        data['Topic'] = '"%s"' % abstract.getTopic() or ''



        
