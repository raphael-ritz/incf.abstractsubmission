"""Definition of the Abstract content type
"""

try:
    import json
except ImportError:  # python <= 2.4
    import simplejson as json

from urllib import urlopen
from StringIO import StringIO

from zope.interface import implements
from DateTime import DateTime
from Products.CMFCore.permissions import ReviewPortalContent

from Products.Archetypes import atapi
from Products.ATContentTypes.content import base
from Products.ATContentTypes.content import schemata

from Products.MasterSelectWidget.MasterSelectWidget import MasterSelectWidget

from Products.ATExtensions import ateapi
from Products.ATExtensions.Extensions.utils import getDisplayList

#from Products.WorkflowField import WorkflowField

from incf.abstractsubmission.interfaces import IAbstract
from incf.abstractsubmission.config import PROJECTNAME

AbstractSchema = schemata.ATContentTypeSchema.copy() + atapi.Schema((
    ateapi.CommentField('intro',
                        comment= "Submitted abstracts can be modified until "\
                        "the deadline - April 27, 2011. ",
                        ),
    ateapi.RecordsField('authors',
                        searchable=1,
                        index_method='formatAuthors',
                        required=1,
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
                                        'affiliation': 60,
                                        },
                        subfield_maxlength={'firstnames':120,
                                            'lastname':120,
                                            'email':120,
                                            'affiliation':120,
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
                        description="We ask you to keep the abstract length "\
                        "to around one page (A4 or US letter) or less, including image. ",
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
                                                # as long as we use a MasterSelectWidget we cannot use 'radio'
                                                format="radio",
                                                slave_fields=({'name':'whyDemo',
                                                               'action': 'show',
                                                               'hide_values': ('Demo',),
                                                               },
                                                              ),
                                                ),
                      ),
    atapi.TextField('whyDemo',
                    widget=atapi.TextAreaWidget(label="Why Demo?",
                                                description="If you have chosen 'Demo' "\
                                                "above: Please give a "\
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
    atapi.BooleanField('travelAward',
                       widget=atapi.BooleanWidget(label='Travel Award',
                                                  description='Check box if you would '\
                                                  'like to be considered for the '\
                                                  'student/post-doctoral travel award. '\
                                                  '(<a href="/about/travel-awards" target="_blank">'\
                                                  'Information on eligibility and requirements</a>)',
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
    ## WorkflowField('submit',
    ##               write_permissiom=ReviewPortalContent,
    ##               ),
    ateapi.CommentField('closing',
                        comment= \
                        "Submitted abstracts can be modified until the "\
                        "deadline - April 27, 2011."),
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
                                             "or PNG and cannot be bigger than 5MB. In the "\
                                             "final display the image will be scaled "\
                                             "to the size chosen below."
AbstractSchema['identifier'].widget.description = "Identifier to be "\
    "used in the program and abstract booklet."
## AbstractSchema['submit'].widget.label="Reviewers"
## AbstractSchema['submit'].widget.description = "How did you decide to treat this abstract? "\
##                                               "You need to press 'submit' below for this to take effect."

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

atapi.registerType(Abstract, PROJECTNAME)
