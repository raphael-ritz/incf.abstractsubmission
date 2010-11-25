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

    ateapi.FormattableNamesField('authors',
                                 subfields=('firstnames', 
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
                                ),
    atapi.TextField('abstract',
                    searchable=1,
                    primary=1,
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
                      widget=atapi.SelectionWidget(format="radio"),
                      ),
    atapi.TextField('whyDemo',
                    widget=atapi.TextAreaWidget(label="Why Demo?",
                                                description="If you have "\
                    "choosen 'Demo' above: Please give a brief explanation "\
                    "why your contribution would benefit from being demonstrated "\
                    "live rather than by a regular poster presentation.",
                                                ),
                    ),
    atapi.LinesField('topics',
                     multivalued=1,
                     vocabulary='getTopics',
                     widget=atapi.MultiSelectionWidget(format="checkbox"),
                     ),
))

# Set storage on fields copied from ATContentTypeSchema, making sure
# they work well with the python bridge properties.

AbstractSchema['title'].storage = atapi.AnnotationStorage()
AbstractSchema['description'].storage = atapi.AnnotationStorage()
AbstractSchema['description'].schemata = 'categorization'

schemata.finalizeATCTSchema(AbstractSchema, moveDiscussion=False)


class Abstract(base.ATCTContent):
    """Abstract Submission"""
    implements(IAbstract)

    meta_type = "Abstract"
    schema = AbstractSchema

    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')

    def getTopics(self):
        """Available scientific categories"""
        return atapi.DisplayList((('Topic1','Topic1'),
                                  ('Topic2','Topic2'),
                                  )
                                 )

atapi.registerType(Abstract, PROJECTNAME)
