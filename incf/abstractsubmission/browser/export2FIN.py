from StringIO import StringIO
from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName

DEFAULTS = (
    ('Title', ''),   # academic title
    ('Email', ''),
    ('First Name', ''),
    ('Middle Name', ''),
    ('Last Name', ''),
    ('Suffix', ''),
    ('Correspondence Author', 'no'),
    ('Author order Sequence', ''),
    ('Affiliation order Sequence', ''),
    ('Author Affiliation', ''),
    ('Organization Name', ''),
    ('Department', ''),
    ('City', ''),
    ('Zip/Postal Code', ''),
    ('State/Province', ''),
    ('Country', ''),
    ('Abstract Title', ''),
    ('Abstract', ''),
    ('Presentation Type', ''),
    ('Topic', ''),
    ('Acknowledgements', ''),
    ('Keywords', ''),
    ('Conflict of Interest', 'no'),
    )

KEYS = [t[0] for t in DEFAULTS]

class Export(BrowserView):
    """Support export to Frontiers in Neuroinformatics"""

    def export2fin(self, delimiter='|', newline='\r\n', testing=None):
        """CSV export using a schema from FIN"""

        out = StringIO()
        out.write(delimiter.join(KEYS) + newline)

        abstracts = self.getAbstracts(testing=testing)

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
            return abstracts[:5]
        else:
            return abstracts

    def addEntry(self, data, index, author, abstract):

        author_index = str(index + 1)
        affiliation_index = str(author.get('affiliation_index'))

        data['Email'] = author.get('email') or ''
        data['First Name'] = author.get('firstnames') or ''
        data['Last Name'] = author.get('lastname') or ''
        if index == 0:
            data['Correspondence Author'] = 'yes'
        data['Author order Sequence'] = author_index
        data['Affiliation order Sequence'] = affiliation_index
        data['Author Affiliation'] = "%s*%s" % (author_index, affiliation_index)
        data['Organization Name'] = author.get('affiliation') or ''
        data['Abstract Title'] = abstract.Title()
        data['Presentation Type'] = abstract.getPresentationFormat() or ''
        data['Topic'] = abstract.getTopic() or ''



        
