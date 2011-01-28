from Acquisition import aq_inner
from Products.CMFCore.permissions import ReviewPortalContent
from Products.CMFCore.utils import _checkPermission
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.browser.ploneview import Plone
from zope.component.interfaces import ComponentLookupError

class IncfPlone(Plone):
    """ Override to manipulate the 'editable order'
    """

    def showEditableBorder(self):
        """Determine if the editable border should be shown - overridden 
        to catch our exceptions
        """

        exceptions = ['abstracts',
                      ]

        exception = False

        context = aq_inner(self.context)
        context_url = context.absolute_url()

        for e in exceptions:
            if context_url.endswith(e):
                exception = True
        
        portal_membership = getToolByName(context, 'portal_membership')
        checkPerm = portal_membership.checkPermission

        if exception and not checkPerm('Review portal content', context):
            return False

        return Plone.showEditableBorder(self)
