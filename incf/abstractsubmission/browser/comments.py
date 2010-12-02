from Acquisition import aq_inner, aq_parent
from AccessControl import getSecurityManager
from Products.CMFCore.utils import getToolByName
from Products.CMFDefault.DiscussionTool import DiscussionNotAllowed

from plone.app.layout.viewlets.comments import CommentsViewlet as ViewletBase


class CommentsViewlet(ViewletBase):
    """overriding 'get_replies' to add a 
    security check for the View permission, 
    so that people who have view rights to the content item
    can see it even if they do not have rights to see the 
    comments on that item"""

    
    def get_replies(self):
        replies = []

        context = aq_inner(self.context)
        container = aq_parent(context)
        pd = self.portal_discussion
        sm = getSecurityManager()

        def getRs(obj, replies, counter):
            rs = pd.getDiscussionFor(obj).getReplies()
            if len(rs) > 0:
                rs.sort(lambda x, y: cmp(x.modified(), y.modified()))
                for r in rs:
                    if sm.checkPermission('View', r):
                        replies.append({'depth':counter, 'object':r})
                        getRs(r, replies, counter=counter + 1)

        try:
            getRs(context, replies, 0)
        except DiscussionNotAllowed:
            # We tried to get discussions for an object that has not only
            # discussions turned off but also no discussion container.
            return []
        return replies
