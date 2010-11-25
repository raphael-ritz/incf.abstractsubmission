"""Definition of the SubmissionFolder content type
"""

from zope.interface import implements

from Products.Archetypes import atapi
from Products.ATContentTypes.content import folder
from Products.ATContentTypes.content import schemata

# -*- Message Factory Imported Here -*-

from incf.abstractsubmission.interfaces import ISubmissionFolder
from incf.abstractsubmission.config import PROJECTNAME

SubmissionFolderSchema = folder.ATFolderSchema.copy() + atapi.Schema((

    # -*- Your Archetypes field definitions here ... -*-

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


class SubmissionFolder(folder.ATFolder):
    """Container for Abstract submissions"""
    implements(ISubmissionFolder)

    meta_type = "SubmissionFolder"
    schema = SubmissionFolderSchema

    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')

    # -*- Your ATSchema to Python Property Bridges Here ... -*-

atapi.registerType(SubmissionFolder, PROJECTNAME)
