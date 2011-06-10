from StringIO import StringIO
from Products.Five.browser import BrowserView

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

    def export2fin(self, delimiter='|', newline='\r\n'):
        """CSV export using a schema from FIN"""

        data = dict(DEFAULTS)
        out = StringIO()
        out.write(delimiter.join(KEYS) + newline)

        value = out.getvalue()
        out.close()
        self.request.RESPONSE.setHeader('Content-Type', 'application/x-msexcel')
        self.request.RESPONSE.setHeader("Content-Disposition", 
                                        "inline;filename=INCF2011abstracts.csv")

        return value

        

        
