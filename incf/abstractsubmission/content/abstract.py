"""Definition of the Abstract content type
"""

try:
    import json
except ImportError:  # python <= 2.4
    import simplejson as json

from urllib import urlopen
from StringIO import StringIO

from PIL import Image

from zope.interface import implements
from DateTime import DateTime
from Products.CMFCore.permissions import ModifyPortalContent
from Products.CMFCore.permissions import ReviewPortalContent

from Products.Archetypes import atapi
from Products.ATContentTypes.content import base
from Products.ATContentTypes.content import schemata

from Products.ATExtensions import ateapi
from Products.ATExtensions.Extensions.utils import getDisplayList

from incf.abstractsubmission.interfaces import IAbstract
from incf.abstractsubmission.config import PROJECTNAME

MINIMUM_IMAGE_SIZE = 600  # number of pixel of shorter image dimension
SUPPORTED_IMAGE_FORMATS = ('jpg', 'jpeg', 'png', 'gif')


AbstractSchema = schemata.ATContentTypeSchema.copy() + atapi.Schema((
    ateapi.CommentField('intro',
                        comment_method="introComment",
                        comment= "Submitted abstracts can be modified until "\
                        "the deadline. ",
                        ),
    ateapi.RecordsField('authors',
                        searchable=1,
                        index_method='formatAuthors',
                        required=1,
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
                        subfield_sizes={'firstnames': 10,
                                        'lastname': 15,
                                        'email': 15,
                                        'affiliation': 30,
                                        },
                        subfield_maxlength={'firstnames':120,
                                            'lastname':120,
                                            'email':120,
                                            'affiliation':200,
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
                    allowable_content_types=('text/x-web-intelligent',),
                    widget=atapi.TextAreaWidget(
                        rows=20,
                        description="Plain text only. Text length is restricted to 2000 characters maximum. "\
                        "References should include DOIs if possible. "\
                        "Text will be rendered as entered preserving whitespace "\
                        "and embedded links will be clickable. Mathematical expressions "\
                        "are not supported. Put them in the image if needed.",
                        maxlength=2000,  
                        ),
                    ),
    atapi.StringField('acknowledgments',
                      widget=atapi.TextAreaWidget(label="Acknowledgments",
                                                  rows=5,maxlength=300),
                      ),
    atapi.TextField('citations',
                    default_output_type='text/x-html-safe',
                    allowable_content_types=('text/x-web-intelligent',),                      
                    widget=atapi.TextAreaWidget(label="References",
                                                rows=10,maxlength=500),
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
                      default='large',
                      widget=atapi.SelectionWidget(label="Image Size",
                                                   format='radio',
                                                   visible={'view': 'invisible', 'edit': 'invisible'},
                                                   description='The image will be scaled such '\
                                                   'that its dimensions are not larger than the selection. '\
                                                   'The aspect ratio will be preserved.',
                                                   ),
                      ),
    atapi.StringField('presentationFormat',
                      vocabulary=atapi.DisplayList((('Poster', 'Poster'),
                                                    ('Demo', 'Talk or Poster'))),
                      default='Poster',
                      widget=atapi.SelectionWidget(label="Preferred "\
                                                   "Presentation Format",
                                                   description='The default presentation format '\
                                                   'is "Poster". If you want your abstract to be '\
                                                   'considered for an oral presentation, please '\
                                                   'select the "Talk or Poster" option.',
                                                   format="radio",
                                             ),
                      ),
    atapi.StringField('whyDemo',
                        view_permission=ModifyPortalContent,
                        widget=atapi.TextAreaWidget(label="Why Talk?",
                                                    description="If you have chosen 'Talk' "\
                                                    "above: Please give a "\
                                                    "brief explanation of "\
                    "why your contribution should be selected for an oral presentation.",
                    ),
                    ),
    atapi.StringField('topic',
                      vocabulary='getTopics',
                      required=0,
                      widget=atapi.SelectionWidget(format="radio",
                                                   condition="object/getTopics",
                                                   ),
                      ),
    atapi.LinesField('sessionType',
                     multivalued=True,
                     vocabulary='getSessionTypes',
                     default=['Poster Session'],
                     write_permission=ReviewPortalContent,
                     widget=atapi.MultiSelectionWidget(format="checkbox"),
                     ),
    atapi.StringField('identifier',
                      searchable=True,
                      write_permission=ReviewPortalContent,
                      ),
    ateapi.CommentField('closing',
                        comment_method = 'closingComment',
                        comment= \
                        "Submitted abstracts can be modified until the "\
                        "deadline."),
))

# Set storage on fields copied from ATContentTypeSchema, making sure
# they work well with the python bridge properties.

AbstractSchema['title'].storage = atapi.AnnotationStorage()
AbstractSchema['description'].storage = atapi.AnnotationStorage()
AbstractSchema['description'].schemata = 'categorization'
AbstractSchema['authors'].widget.description = "Please add "\
                                               "additional authors in the order in "\
                                               "which they should be displayed."
AbstractSchema['image'].widget.description = "You have the option to include "\
                                             "one image with your abstract. This image "\
                                             "should be in one of the formats GIF, JPG, "\
                                             "or PNG and should be at least 700 pixels wide "\
                                             "and no larger than 5MB. "
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

    # class defaults
    _notified = None

    def Description(self):
        """Override description accessor to return author list"""
        return self.formatAuthors()

    def Subject(self):
        """Override subject to return topic"""
        return [self.getTopic()]

    def introComment(self):
        """To be shown on top of the edit form"""
        return self.aq_parent.getIntroductoryComment()

    def closingComment(self):
        """To be shown at the end of the edit form"""
        return self.aq_parent.getClosingComment()

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

        return [{'firstnames': '(your first names)',
                 'lastname': '(your last name)',
                 'email': 'you@somewhere.com',
                 'affiliation': 'Some Great Place',
                 },]

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

    def hasImage(self):
        """True if an image has been uploaded, False otherwise"""
        img = self.getField('image').getRaw(self)
        if img == '':    # yes, '' is the default value of an image field
             return False
        return True

    def tag(self, **kwargs):
        """Generate image tag using the api of the ImageField
        """
        return self.getField('image').tag(self, **kwargs)

    def notified(self):
        """Date of last notification or None"""
        return self._notified

    def setNotificationDate(self):
        """Sets notification date to current time"""
        self._notified = DateTime()

    # for the abstract book

    def getPlainText(self, escape_quote=False):
        """helper method for custom plain text formating"""
        text = self.getAbstract(mimetype='text/plain')
        dummy = '%$%$%'
        text = text.replace('&nbsp;', ' ')   # in case this survived
        text = text.replace(' \r\n ', dummy)
        text = text.replace('\r\n', ' ')
        text = text.replace(dummy, ' \r\n ')
        if escape_quote:
            text = text.replace('"', '""')
        
        return self.normalizeWhitespace(text)

    def normalizeWhitespace(self, text, separator='\r\n'):
        lines = []
        for line in StringIO(text):
            l = line.strip()
            if not l:    # skip empty lines
                continue
            while '  ' in l:
                l = l.replace('  ', ' ')
            lines.append(l)
        return separator.join(lines)

    def getAuthorAndAffiliationInfo(self):
        """Helper method to cast the author info into something more consumable"""

        authors = self.getAuthors()
        # get the trivial case out of the way
        if len(authors) == 1:
            authorstring = "%(firstnames)s %(lastname)s" % authors[0]
            affiliation = authors[0].get('affiliation')
            return authorstring, [affiliation]

        affiliations = [a.get('affiliation') for a in authors]
        # all affiliations the same
        if len(set(affiliations)) == 1:
            authorstring = self.getAuthorsString(authors, addNumbers=False)
            affiliation = authors[0].get('affiliation')
            return authorstring, [affiliation]

        authors = self.addAffiliationIndex(authors, affiliations)

        # several authors, several affiliations
        authorstring = self.getAuthorsString(authors, addNumbers=True)
        affiliationlist = self.getAffiliationList(affiliations)
        return authorstring, affiliationlist

    def getAuthorsString(self, authors, addNumbers=False):
        if addNumbers:
            authorlist = ["%(firstnames)s %(lastname)s%(affiliation_index)s" % a \
                          for a in authors]
        else:
            authorlist = ["%(firstnames)s %(lastname)s" % a for a in authors]
        # the trivial case - one author is handled already
        if len(authorlist) == 2:
            return ' and '.join(authorlist)
        l1 = authorlist[:-1]
        return ', '.join(l1) + ' and ' + authorlist[-1]

    def addAffiliationIndex(self, authors, affiliations=None):
        if affiliations is None:
            affiliations = [a.get('affiliation') for a in authors]
        index_map = self.getAffiliationList(affiliations, mapping = True)
        for a in authors:
            a['affiliation_index'] = index_map[a.get('affiliation')]
        return authors   # assuming the change is picked up

    def getAffiliationList(self, affiliations, mapping=False):
        """Filter out duplicates and add numbers in front.
        If 'mapping' is true, return a dictionary
        'affiliation' -> 'index' instead"""
        seen = []
        result = []
        index = 0
        result_map = {}
        for a in affiliations:
            if a not in seen:
                seen.append(a)
                index += 1
                result.append('%s. %s' % (index, a))
                result_map[a] = index
        return mapping and result_map or result

    def abstractBookSource(self, separator='\r\n\r\n'):
        """Custom plain text format to be consumed by Malin and Helena"""

        lines = []
        lines.append("%s %s" % (self.getIdentifier(), self.Title()))
        #lines.append(self.formatAuthors())  # uncomment for sanity checking 
        authors, affiliations = self.getAuthorAndAffiliationInfo()
        lines.append('\r\n'.join([authors]+affiliations))
        lines.append(self.getPlainText())
        if self.getImage():
            lines.append("%s_image\r\n%s\r\n" % (self.getIdentifier(),
                                                 self.getImageCaption()))

        return separator.join(lines)

    # helper message for sanity checking of the image
    def checkImageFormat(self, request):
        """Called from 'validate_integrity'. Return a warning phrase if the
        image seems fishy"""

        image_upload = request.form.get('image_file', None) 
        if image_upload is not None:
            image_upload.seek(0)
            image = Image.open(image_upload)
            if image.format.lower() not in SUPPORTED_IMAGE_FORMATS:
                return "Image format '%s' is not supported. Please consider uploading "\
                    "a JPG, GIF or PNG file." % image.format
            if min(image.size) < MINIMUM_IMAGE_SIZE:
                return "The image size of %sx%s will be too small for the printed abstract book. "\
                    "Please double-check and consider uploading a larger "\
                    "or higher resolution image." % (image.size[0], image.size[1])

        return None  # everything OK

atapi.registerType(Abstract, PROJECTNAME)
