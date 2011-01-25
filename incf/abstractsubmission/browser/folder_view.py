from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName

class FolderView(BrowserView):
    """Various UI methods"""

    @property
    def catalog(self):
        return getToolByName(self.context, 'portal_catalog')
    
    @property
    def isAnonymous(self):
        """True if user is anonymous False otherwise"""
        membertool = getToolByName(self.context, 'portal_membership')
        return membertool.isAnonymousUser()

    def getAbstractsByTopic(self, topic):
        """All abstracts for a given topic"""
        return self.catalog(portal_type="Abstract", 
                            Subject=topic,
                            sort_on="created",
                            )   # XXX maybe add a path constraint?

    def getAbstractsForCurrentMember(self):
        """Look up abstract submissions for the current user """
        membertool = getToolByName(self.context, 'portal_membership')
        userid = membertool._getSafeMemberId()
        return self.catalog(portal_type='Abstract',
                            Creator=userid,
                            )

    def profileUrl(self):
        """URL to profile page at main site for current user"""
        membertool = getToolByName(self.context, 'portal_membership')
        userid = membertool._getSafeMemberId()
        return "http://www.incf.org/community/people/%s" % userid

# XXX should we @memoize this?
    def getTopicCount(self, topic):
        """number of abstracts for the topic given"""

        return len(self.catalog(portal_type="Abstract", 
                                Subject=topic,
                                )
                   )


    def headline(self, topic):
        """Name of topic followed by abstract count in parentheses"""
        return "%s (%s)" % (topic, self.getTopicCount(topic))
