from Products.CMFCore import permissions as CMFCorePermissions
from AccessControl.SecurityInfo import ModuleSecurityInfo
from Products.CMFCore.permissions import setDefaultRoles

security = ModuleSecurityInfo('incf.abstractsubmission')
security.declarePublic('AbstractSubmissionCSVExport')
AbstractSubmissionCSVExport = 'AbstractSubmission: CSVExport'
setDefaultRoles(AbstractSubmissionCSVExport, ('Manager', 'Owner'))
