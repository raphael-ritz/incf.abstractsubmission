"""Definition of the SubmissionFolder content type
"""

from StringIO import StringIO

from zope.interface import implements
from contentratings.interfaces import IUserRating

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
            # handle comments
            reply_count = abstract.portal_discussion.getDiscussionFor(abstract).replyCount(abstract)
            replies = abstract.portal_discussion.getDiscussionFor(abstract).getReplies()
            if not replies:
                comments = 'None'
            else:
                comments = []
                for r in replies:
                    comments.append("%s (%s): %s - %s" % (r.Creator(),
                                                          r.created().Date(),
                                                          r.Title(),
                                                          r.CookedBody()))
                comments = " -- ".join(comments)
            values = [abstract.getAuthors()[0].get('firstnames'),
                      abstract.getAuthors()[0].get('lastname'),
                      abstract.getAuthors()[0].get('email'),
                      abstract.getAuthors()[0].get('affiliation'),
                      abstract.Country(),
                      abstract.Title(),
                      abstract.getPresentationFormat(),
                      abstract.getTopic(),
                      str(abstract.getTravelAward() or False),
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
                      

atapi.registerType(SubmissionFolder, PROJECTNAME)
