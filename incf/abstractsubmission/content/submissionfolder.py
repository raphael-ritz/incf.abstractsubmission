"""Definition of the SubmissionFolder content type
"""

from StringIO import StringIO

from zope.interface import implements

from Products.Archetypes import atapi
from Products.ATContentTypes.content import folder
from Products.ATContentTypes.content import schemata

# -*- Message Factory Imported Here -*-

from incf.abstractsubmission.interfaces import ISubmissionFolder
from incf.abstractsubmission.config import PROJECTNAME

SubmissionFolderSchema = folder.ATBTreeFolderSchema.copy() + atapi.Schema((
    atapi.TextField('introduction',
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

schemata.finalizeATCTSchema(
    SubmissionFolderSchema,
    folderish=True,
    moveDiscussion=False
)


class SubmissionFolder(folder.ATBTreeFolder):
    """Container for Abstract submissions"""
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
                'Poster',
                'Demo',
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
                  'session',
                  'url',
                  ]
        out = StringIO()
        out.write(delimiter.join(fields) + newline)
        for abstract in abstracts:
            values = [abstract.getAuthors()[0].get('firstnames'),
                      abstract.getAuthors()[0].get('lastname'),
                      abstract.getAuthors()[0].get('email'),
                      abstract.getAuthors()[0].get('affiliation'),
                      abstract.Country(),
                      abstract.Title(),
                      abstract.getPresentationFormat(),
                      abstract.getSessiontype(),
                      abstract.absolute_url(),
                      ]
            out.write(delimiter.join(values) + newline)
        value = out.getvalue()
        out.close()
        self.REQUEST.RESPONSE.setHeader('Content-Type', 'application/x-msexcel')
        self.REQUEST.RESPONSE.setHeader("Content-Disposition", 
                                        "inline;filename=congress2010abstracts.csv")

        return value
                      

atapi.registerType(SubmissionFolder, PROJECTNAME)
