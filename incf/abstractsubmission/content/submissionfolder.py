"""Definition of the SubmissionFolder content type
"""

from zope.interface import implements

from Products.Archetypes import atapi
from Products.ATContentTypes.content import folder
from Products.ATContentTypes.content import schemata

# -*- Message Factory Imported Here -*-

from incf.abstractsubmission.interfaces import ISubmissionFolder
from incf.abstractsubmission.config import PROJECTNAME

SubmissionFolderSchema = folder.ATBTreeFolderSchema.copy() + atapi.Schema((

    atapi.LinesField('topics',
                     default_method="getDefaultTopics",
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

atapi.registerType(SubmissionFolder, PROJECTNAME)
