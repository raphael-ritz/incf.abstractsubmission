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
                                ),
    atapi.TextField('abstract'),
    atapi.StringField('presentationFormat',
                      vocabulary=atapi.DisplayList((('Poster', 'Poster'),
                                                    ('Demo', 'Demo'))),
                      default='Poster',
                      widget=atapi.SelectionWidget(format="radio"),
                      ),
    atapi.LinesField('topics',
                     multivalued=1,
                     vocabulary='getTopics',
                     widget=atapi.MultiSelectionWidget(),
                     ),
))

# Set storage on fields copied from ATContentTypeSchema, making sure
# they work well with the python bridge properties.

AbstractSchema['title'].storage = atapi.AnnotationStorage()
AbstractSchema['description'].storage = atapi.AnnotationStorage()

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
