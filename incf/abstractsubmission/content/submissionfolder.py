"""Definition of the SubmissionFolder content type
"""

from StringIO import StringIO

from zope.interface import implements
from contentratings.interfaces import IUserRating

from AccessControl import ClassSecurityInfo
from Products.CMFCore.permissions import ManagePortal
from Products.CMFCore.utils import getToolByName

from Products.Archetypes import atapi
from Products.ATContentTypes.content import folder
from Products.ATContentTypes.content import schemata

# -*- Message Factory Imported Here -*-

from incf.abstractsubmission.interfaces import ISubmissionFolder

from incf.abstractsubmission.config import PROJECTNAME
from incf.abstractsubmission.config import INTRO_CLOSED
from incf.abstractsubmission.config import INTRO_OPEN_ANONYMOUS
from incf.abstractsubmission.config import INTRO_OPEN_AUTHENTICATED


SubmissionFolderSchema = folder.ATBTreeFolderSchema.copy() + atapi.Schema((
    atapi.BooleanField('open'),
    atapi.TextField('introductionClosed',
                    default=INTRO_CLOSED,
                    default_output_type='text/html',
                    allowable_content_types=('text/plain',
                                             'text/structured',
                                             'text/html'),
                    widget=atapi.RichWidget(),
                    ),
    atapi.TextField('introductionOpenAnonymous',
                    default=INTRO_OPEN_ANONYMOUS,
                    default_output_type='text/html',
                    allowable_content_types=('text/plain',
                                             'text/structured',
                                             'text/html'),
                    widget=atapi.RichWidget(),
                    ),
    atapi.TextField('introductionOpenAuthenticated',
                    default=INTRO_OPEN_AUTHENTICATED,
                    default_output_type='text/html',
                    allowable_content_types=('text/plain',
                                             'text/structured',
                                             'text/html'),
                    widget=atapi.RichWidget(),
                    ),
    atapi.LinesField('topics',
                     default_method="getDefaultTopics",
                     widget=atapi.LinesWidget(description="Define the terms "\
                     "to be offered for the abstract classification here. "\
                     "One term per line."),
                     ),
    atapi.LinesField('sessionTypes',
                     default_method="getDefaultSessionTypes",
                     widget=atapi.LinesWidget(description="Define the "\
                     "session types to be offered for the presenations here. "\
                     "One term per line."),
                     ),
    atapi.StringField('introductoryComment',
                       default="Abstracts can be updated until the deadline.",
                       widget=atapi.TextAreaWidget(
                           label="Introductory Comment",
                           description="Shown on top of the abstract's edit "\
                           "form (format: structured text).",
                           rows=3),
                     ),
    atapi.StringField('closingComment',
                       default="Abstracts can be updated until the deadline.",
                       widget=atapi.TextAreaWidget(
                           label="Closing Comment",
                           description="Shown at the end of the abstract's "\
                           "edit form (format: structured text).",
                           rows=3),
                     ),
))

# Set storage on fields copied from ATFolderSchema, making sure
# they work well with the python bridge properties.

SubmissionFolderSchema['title'].storage = atapi.AnnotationStorage()
SubmissionFolderSchema['description'].storage = atapi.AnnotationStorage()
SubmissionFolderSchema['open'].widget.description="Tick to open abstract "\
    "submission and untick to close it."
SubmissionFolderSchema['introductionClosed'].widget.label = "Introduction (i)"
SubmissionFolderSchema['introductionClosed'].widget.description = \
    "This text is shown if abstract submission is closed."
SubmissionFolderSchema['introductionOpenAnonymous'].widget.label = "Introduction (ii)"
SubmissionFolderSchema['introductionOpenAnonymous'].widget.description = \
    "This text is shown if abstract submission is open and the user is "\
    "anonymous. Following the text a register and login button are offered."
SubmissionFolderSchema['introductionOpenAuthenticated'].widget.label = "Introduction (iii)"
SubmissionFolderSchema['introductionOpenAuthenticated'].widget.description = \
    "This text is shown if abstract submission is open and the user is "\
    "authenticated. Following the text a 'create new' and 'view exisiting' "\
    "button are offered."


schemata.finalizeATCTSchema(
    SubmissionFolderSchema,
    folderish=True,
    moveDiscussion=False
)


class SubmissionFolder(folder.ATBTreeFolder):
    """Section for Abstract submissions"""
    implements(ISubmissionFolder)

    security = ClassSecurityInfo()

    meta_type = "SubmissionFolder"
    schema = SubmissionFolderSchema

    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')

    def getDefaultTopics(self):
        """Hard coded list of default topics"""
        return ('General neuroinformatics',
                'Computational neuroscience',
                'Digital atlasing',
                'Neuroimaging',
                'Genomics and genetics',
                'Large scale modeling',
                'Neuromorphic engineering',
                'Brain machine interface',
                'Electrophysiology',
                'Infrastructural and portal services',
                'Clinical neuroscience',
                )

    def getDefaultSessionTypes(self):
        """Hard coded list of default session types"""
        return ('Keynote',
                'Workshop 1',
                'Workshop 2',
                'Workshop 3',
                'Workshop 4',
                'US Node Session',
                'Spotlight Presentation',
                'Poster Session',
                'Demo Session',
                )

    def csv(self, delimiter='|', newline='\n\r'):
        """Export abstracts in csv format"""
        abstracts = self.contentValues()
        fields = ['firstnames',
                  'lastname',
                  'email',
                  'affiliation',
                  'country',
                  'title',
                  'format',
                  'topic',
                  'travelaward',
                  'session',
                  'url',
                  'rating',
                  '#replies',
                  'comments',
                  ]
        out = StringIO()
        out.write(delimiter.join(fields) + newline)
        for abstract in abstracts:
            # handle ratings
            rated = IUserRating(abstract)
            average = float(rated.averageRating)
            number = rated.numberOfRatings
            rating = "%2.2f (%s)" % (average, number)
            reply_count, comments = comment_data(abstract)
            values = [abstract.getAuthors()[0].get('firstnames') or '',
                      abstract.getAuthors()[0].get('lastname') or '',
                      abstract.getAuthors()[0].get('email') or '',
                      abstract.getAuthors()[0].get('affiliation') or '',
                      abstract.Country() or '',
                      abstract.Title() or '',
                      abstract.getPresentationFormat() or '',
                      abstract.getTopic() or '',
                      #str(abstract.getTravelAward() or False),
                      ', '.join(abstract.getSessionType()),
                      abstract.absolute_url(),
                      rating,
                      str(reply_count),
                      comments,
                      ]
            out.write(delimiter.join(values) + newline)
        value = out.getvalue()
        out.close()
        self.REQUEST.RESPONSE.setHeader('Content-Type', 'application/x-msexcel')
        self.REQUEST.RESPONSE.setHeader("Content-Disposition", 
                                        "inline;filename=congress2011abstracts.csv")

        return value

    def displayContentsTab(self):
        """Suppress the default Contents tab"""
        return False

    security.declareProtected(ManagePortal, 'setSessionFromId')
    def setSessionFromId(self):
        """Helper method inferring session from given id.
        Based on heuristics applicable at the time of writing
        Warning: this resets the session(s) assigned"""

        abstracts = self.contentValues()
        for abstract in abstracts:
            id = abstract.getIdentifier()
            if not id:
                continue
            id = id.lower()
            if id.startswith('d'):
                abstract.setSessionType(['Demo Session'])
            elif id[-1] in ['0','2','4','6','8']:
                abstract.setSessionType(['Poster Session 2'])
            else:
                abstract.setSessionType(['Poster Session 1'])

    security.declareProtected(ManagePortal, 'notifyAllAccepted')
    def notifyAllAccepted(self):
        """Notify authors of ALL accepted abstracts that have not been
        notified yet by triggering the 'notify' transition"""

        template = "****** Notified author of %s - <a href='%s'>%s</a><br />\n"

        out = StringIO()
        wft = getToolByName(self, 'portal_workflow')
        abstracts = self.contentValues()
        
        for abstract in abstracts:
            state = wft.getInfoFor(abstract, 'review_state')
            if state not in ['accepted']:
                out.write("not accepted: skipping %s<br />\n" % abstract.absolute_url())
                continue
            notified = abstract.notified()
            if notified is not None:
                out.write("already notified: skipping %s<br />\n" % abstract.absolute_url())
                continue
            wft.doActionFor(abstract, 'notify')
            out.write(template % (abstract.getIdentifier(),
                                  abstract.absolute_url(),
                                  abstract.Title(),
                                  ))
        value = out.getvalue()
        out.close()
        return value

def comment_data(abstract):
    """Helper function returning the number and concatenated text
    of comments made on 'abstract'"""
    # try old API first
    try:
        reply_count = abstract.portal_discussion.getDiscussionFor(abstract).replyCount(abstract)
        replies = abstract.portal_discussion.getDiscussionFor(abstract).getReplies()
        if not replies:
            return 0, 'None'
        comments = []
        for r in replies:
            comments.append("%s (%s): %s - %s" % (r.Creator(),
                                                   r.created().Date(),
                                                   r.Title(),
                                                   r.CookedBody()))
        comments = " -- ".join(comments)
        return reply_count, comments
    except AttributeError:
        # usually happens if plone.app.discussion is used
        # then the following should work
        from plone.app.discussion.interfaces import IConversation
        conversation = IConversation(abstract)
        reply_count = len(conversation.objectIds())
        if not reply_count:
            return 0, 'None'        
        replies = [conversation[id] for id in conversation.objectIds()]
        comments = []
        for r in replies:
            comments.append("%s (%s): %s" % (r.author_name,
                                              r.modification_date.strftime('%Y-%m-%d %H:%M'),
                                              r.text))
        comments = " -- ".join(comments)
        return reply_count, comments.encode('utf-8')            


atapi.registerType(SubmissionFolder, PROJECTNAME)
