"""Definition of the Abstract content type
"""

try:
    import json
except ImportError:  # python <= 2.4
    import simplejson as json

from urllib import urlopen

from zope.interface import implements

from Products.CMFCore.permissions import ReviewPortalContent

from Products.Archetypes import atapi
from Products.ATContentTypes.content import base
from Products.ATContentTypes.content import schemata

from Products.ATExtensions import ateapi
from Products.ATExtensions.Extensions.utils import getDisplayList

# -*- Message Factory Imported Here -*-

from incf.abstractsubmission.interfaces import IAbstract
from incf.abstractsubmission.config import PROJECTNAME

AbstractSchema = schemata.ATContentTypeSchema.copy() + atapi.Schema((

    ateapi.RecordsField('authors',
                        subfields=('firstnames', 
                                   'lastname', 
                                   'email',
                                   'affiliation',
                                   'country',
                                   ),
                        required_subfields=('firstnames', 
                                            'lastname', 
                                            'email',
                                            'affiliation',
                                            'country',
                                            ),
                        subfield_sizes={'firstnames': 15,
                                        'lastname': 20,
                                        'email': 20,
                                        'affiliation': 20,
                                        },
                        subfield_vocabularies={'country':'CountryNames'},
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
    atapi.ImageField('image'),
    atapi.StringField('imageCaption',
                      widget=atapi.TextAreaWidget(label="Image Caption",
                                                  rows=3),
                      ),
#    atapi.ComputedField('size',
#                        expression="object/getTextSize",
#                        ),
    atapi.StringField('presentationFormat',
                      vocabulary=atapi.DisplayList((('Poster', 'Poster'),
                                                    ('Demo', 'Demo'))),
                      default='Poster',
                      widget=atapi.SelectionWidget(label="Preferred "\
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
                      widget=atapi.SelectionWidget(format="radio"),
                      ),
    atapi.StringField('sessionType',
                      vocabulary='getSessionTypes',
                      default='Poster Session',
                      write_permission=ReviewPortalContent,
                      widget=atapi.SelectionWidget(format="radio"),
                      ),
))

# Set storage on fields copied from ATContentTypeSchema, making sure
# they work well with the python bridge properties.

AbstractSchema['title'].storage = atapi.AnnotationStorage()
AbstractSchema['description'].storage = atapi.AnnotationStorage()
AbstractSchema['description'].schemata = 'categorization'
AbstractSchema['image'].widget.description = "An optional image to be "\
    "displayed following the text (recommended size: ??x??)"

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

    def Description(self):
        """Override description accessor to return author list"""
        return self.formatAuthors()

    
    def formatAuthors(self, separator = "<br />"):
        
        authors = self.getAuthors()
        strings = []
        for author in authors:
            strings.append("%s %s (%s, %s)" % (author.get('firstnames'),
                                               author.get('lastname'),
                                               author.get('email'),
                                               author.get('affiliation'),
                                               ))
        return separator.join(strings)

    def CountryNames(self, instance):
        """List of all country names (from ATExtensions)"""
        return getDisplayList(self, 'country_names')

    def getTopics(self):
        """Available scientific categories (set on parent folder)"""
        terms = self.aq_parent.getTopics()
        vocab = [(term, term) for term in terms]
        return atapi.DisplayList(vocab)

    def getSessionTypes(self):
        """Available session types (set on parent folder)"""
        terms = self.aq_parent.getSessionTypes()
        vocab = [(term, term) for term in terms]
        return atapi.DisplayList(vocab)

    def defaultAuthor(self):
        """Return data of current user as default for first author"""

        memberId = self.portal_membership.getAuthenticatedMember().getId()
        base_url = "http://incf.org/portal_membership/getMemberInfo"
        url = base_url + "?format=json&memberId=%s" % memberId 
        data = urlopen(url).read()
        if data:
            return [json.loads(data),]
        return [{'firstnames': '(your first name)',
                 'lastname': '(your last name)',
                 'email': 'you@somewhere.com',
                 'affiliation': 'Some Great Place',
                 'country': 'Sweden',
                 },]

    def getTextSize(self):
        """Number of characters of abstract"""
        return len(self.getAbstract(mimetype="text/plain").strip())


atapi.registerType(Abstract, PROJECTNAME)
