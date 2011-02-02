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

from incf.abstractsubmission.interfaces import IAbstract
from incf.abstractsubmission.config import PROJECTNAME

AbstractSchema = schemata.ATContentTypeSchema.copy() + atapi.Schema((
    ateapi.CommentField('intro',
                        comment="You are welcome to submit more than one abstract. "\
                        "The text (plus optional image) of each "\
                        "abstract should fit on one page (A4 or US letter format). "\
                        "Saved abstracts "\
                        "can be modified until the deadline - April 19, 2011"\
                        "**At this time all saved abstracts are considered "\
                        "submitted in the form they are at that time.** You "\
                        "will be notified of the abstract review results by mid May, "\
                        "before the early registration deadline (June 1, 2011)."),
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
                        subfield_sizes={'firstnames': 20,
                                        'lastname': 25,
                                        'email': 30,
                                        'affiliation': 40,
                                        },
                        minimalSize=5,
                        default_method='defaultAuthor',
                        ),
    atapi.TextField('abstract',
                    searchable=1,
                    primary=1,
                    required=1,
                    default_output_type='text/x-html-safe',
                    allowable_content_types=('text/html',),
                    widget=atapi.RichWidget(
                        rows=20,
                        description="Please make sure that your text "\
                        "and image can fit on one A4 or letter-size page. The image will be "\
                        "displayed beneath the text followed by the image caption.",
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
    atapi.StringField('imageSize',
                      vocabulary=atapi.DisplayList((('small', 'Small (200px)'),
                                                    ('default', 'Default (400px)'),
                                                    ('large', 'Large (750px)')
                                                    )),
                      default='default',
                      widget=atapi.SelectionWidget(label="Image Size",
                                                   format='radio',
                                                   description='The image will be scaled such '\
                                                   'that its dimensions are no largeer than the selection. '\
                                                   'The aspect ratio will be preserved.',
                                                   ),
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
                                                description='The default presentation format '\
                                                'is "Poster". If you wish to submit an abstract '\
                                                'for a demonstration, please select the "Demo" '\
                                                'option here.',
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
                                                description="Please give a "\
                                                "brief explanation of "\
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
    ateapi.CommentField('closing',
                        comment="Make sure to save your abstract submission before you leave. "\
                        "Saved abstracts can be modified until the deadline of April 19, 2011.<br /> "\
                        "To return to your abstract, log in to the site and browse "\
                        "to the 'Abstracts' section, or simply click on your name in the "\
                        "upper right-hand corner."),
))

# Set storage on fields copied from ATContentTypeSchema, making sure
# they work well with the python bridge properties.

AbstractSchema['title'].storage = atapi.AnnotationStorage()
AbstractSchema['description'].storage = atapi.AnnotationStorage()
AbstractSchema['description'].schemata = 'categorization'
AbstractSchema['authors'].widget.description = "Information for the first author is "\
                                               "pre-populated from your INCF profile. "\
                                               "Any changes made here it will NOT "\
                                               "be saved to your profile. Please add "\
                                               "additional authors in the order in "\
                                               "which they should be displayed."
AbstractSchema['image'].widget.description = "You have the option to include "\
                                             "one image with your abstract. This image "\
                                             "should be in one of the formats GIF, JPG, "\
                                             "or PNG and cannot be bigger than 5MB. In the "\
                                             "final display the image will be scaled "\
                                             "to the size chosen below."
AbstractSchema['identifier'].widget.description = "Identifier to be "\
    "used in the program and abstract booklet."

schemata.finalizeATCTSchema(AbstractSchema, moveDiscussion=False)
AbstractSchema.moveField('title', after="intro")

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
