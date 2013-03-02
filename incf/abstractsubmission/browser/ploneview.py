from Acquisition import aq_inner
from Products.CMFCore.permissions import ReviewPortalContent
from Products.CMFCore.utils import _checkPermission
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.browser.ploneview import Plone
from zope.component.interfaces import ComponentLookupError

class IncfPlone(Plone):
    """ Override to manipulate the 'editable border'
    """

    def showEditableBorder(self):
        """Determine if the editable border should be shown - overridden 
        to suppress it for regular users on submission folders.
        Since people may add content it would show up otherwise.
        """

        context = aq_inner(self.context)
        if context.getPortalTypeName() != 'SubmissionFolder':
            return Plone.showEditableBorder(self)

        portal_membership = getToolByName(context, 'portal_membership')
        checkPerm = portal_membership.checkPermission

        if not checkPerm('Review portal content', context):
            return False

        return Plone.showEditableBorder(self)
