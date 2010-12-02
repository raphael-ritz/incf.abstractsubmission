"""Definition of the Abstract content type
"""

from zope.interface import implements

from Products.Archetypes import atapi
from Products.ATContentTypes.content import base
from Products.ATContentTypes.content import schemata

from Products.ATExtensions import ateapi

# -*- Message Factory Imported Here -*-

from incf.abstractsubmission.interfaces import IAbstract
from incf.abstractsubmission.config import PROJECTNAME

AbstractSchema = schemata.ATContentTypeSchema.copy() + atapi.Schema((

    ateapi.RecordsField('authors',
                        subfields=('firstnames', 
                                   'lastname', 
                                   'email',
                                   'affiliation',
                                   ),
                        required_subfields=('firstnames', 
                                            'lastname', 
                                            'email',
                                            'affiliation',
                                            ),
                        subfield_sizes={'firstnames': 15,
                                        'lastname': 20,
                                        'email': 20,
                                        'affiliation': 20,
                                        },
                        minimalSize=5,
                        default_method='defaultAuthor',
                        ),
    atapi.TextField('abstract',
                    searchable=1,
                    primary=1,
                    required=1,
                    default_output_type='text/x-html-safe',
                    allowable_content_types=('text/plain',
                                             'text/structured',
                                             'text/html'),
                    widget=atapi.RichWidget(
                #label='Research Focus',
                rows=20,
                #description="The research focus of this group.",
    ),
                    ),
    atapi.StringField('presentationFormat',
                      vocabulary=atapi.DisplayList((('Poster', 'Poster'),
                                                    ('Demo', 'Demo'))),
                      default='Poster',
                      widget=atapi.SelectionWidget(labael="Preferred "\
                                                   "Presentation Format",
                                                   format="radio"),
                      ),
    atapi.TextField('whyDemo',
                    widget=atapi.TextAreaWidget(label="Why Demo?",
                                                description="If you have "\
                    "choosen 'Demo' above: Please give a brief explanation "\
                    "why your contribution would benefit from being demonstrated "\
                    "live rather than by a regular poster presentation.",
                                                ),
                    ),
    atapi.StringField('topic',
                      vocabulary='getTopics',
                      required=1,
                      widget=atapi.SelectionWidget(format="checkbox"),
                      ),
))

# Set storage on fields copied from ATContentTypeSchema, making sure
# they work well with the python bridge properties.

AbstractSchema['title'].storage = atapi.AnnotationStorage()
AbstractSchema['description'].storage = atapi.AnnotationStorage()
AbstractSchema['description'].schemata = 'categorization'

schemata.finalizeATCTSchema(AbstractSchema, moveDiscussion=False)


# hide away some fields for the time being
for field in AbstractSchema.fields():
    if field.schemata != 'default':
        field.widget.visible =  {'view': 'invisible', 'edit': 'invisible'}



class Abstract(base.ATCTContent):
    """Abstract Submission"""
    implements(IAbstract)

    meta_type = "Abstract"
    schema = AbstractSchema

    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')

    def getTopics(self):
        """Available scientific categories"""
        terms = self.aq_parent.getTopics()
        vocab = [(term, term) for term in terms]
        return atapi.DisplayList(vocab)

    def defaultAuthor(self):
        """Return data of current user as default for first author"""
        #XXX TODO
        return [{'firstnames': '(your first name)',
                 'lastname': '(your last name)',
                 'email': 'you@somewhere.com',
                 'affiliation': 'Some Great Place',
                 },]


atapi.registerType(Abstract, PROJECTNAME)
