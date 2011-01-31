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

from Products.MasterSelectWidget.MasterSelectWidget import MasterSelectWidget

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
                        rows=20,
                        description="Please limit your abstract to fit on one page.",
                        filter_buttons=(
                            'bg-indent',
                            'imagelibdrawer-button',
                            'linklibdrawer-button',
                            'anchors-button',
                            'manage-anchors-tab',
                            ),
    ),
                    ),
    atapi.ImageField('image',
                     sizes={'thumb':(80,80),
                            'small':(200,200),
                            'default':(400,400),
                            'large':(750,750),
                            },
                     ),
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
                      widget=MasterSelectWidget(label="Preferred "\
                                                "Presentation Format",
                                                #format="radio",
                                                slave_fields=({'name':'whyDemo',
                                                               'action': 'show',
                                                               'hide_values': ('Demo',),
                                                               },
                                                              ),
                                                ),
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
    atapi.LinesField('sessionType',
                     multivalued=True,
                     vocabulary='getSessionTypes',
                     default=['Poster Session'],
                     write_permission=ReviewPortalContent,
                     widget=atapi.MultiSelectionWidget(format="checkbox"),
                     ),
    atapi.StringField('identifier',
                      write_permission=ReviewPortalContent,
                      ),
))

# Set storage on fields copied from ATContentTypeSchema, making sure
# they work well with the python bridge properties.

AbstractSchema['title'].storage = atapi.AnnotationStorage()
AbstractSchema['description'].storage = atapi.AnnotationStorage()
AbstractSchema['description'].schemata = 'categorization'
AbstractSchema['image'].widget.description = "An optional image to be "\
    "displayed following the text. Formats supported are JPG, GIF, and PNG (recommended size: ??x??)"
AbstractSchema['identifier'].widget.description = "Identifier to be "\
    "used in the program and abstract booklet."

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

    def Subject(self):
        """Override subject to return topic"""
        return [self.getTopic()]

    def formatAuthors(self, separator = ", "):
        
        authors = self.getAuthors()
        strings = []
        for author in authors:
            strings.append("%s %s (%s)" % (author.get('firstnames'),
                                               author.get('lastname'),
                                               author.get('affiliation'),
                                               ))
        return separator.join(strings)

    def CountryNames(self, instance):
        """List of all country names (from ATExtensions)"""
        return getDisplayList(self, 'country_names')

    def Country(self):
        """Country of first author's affiliation
        Set by 'defaultAuthor' on creation"""
        return getattr(self, 'country' , 'unknown')

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

        member = self.portal_membership.getAuthenticatedMember()
        memberId = member.getId()
        memberEmail = member.getProperty('email')
        
        base_url = "http://incf.org/portal_membership/getMemberInfo"
        url = base_url + "?format=json&memberId=%s" % memberId 
        jsondata = urlopen(url).read()
        if jsondata:
            data = json.loads(jsondata)
            self.country = data.get('country','unknown')
            data['email'] = memberEmail
            return [data]

        return [{'firstnames': '(your first names)',
                 'lastname': '(your last name)',
                 'email': 'you@somewhere.com',
                 'affiliation': 'Some Great Place',
                 },]

    def getTextSize(self):
        """Number of characters of abstract"""
        return len(self.getAbstract(mimetype="text/plain").strip())

    def tag(self, **kwargs):
        """Generate image tag using the api of the ImageField
        """
        return self.getField('image').tag(self, **kwargs)


atapi.registerType(Abstract, PROJECTNAME)
