from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName

class FolderView(BrowserView):
    """Various UI methods"""

    @property
    def catalog(self):
        return getToolByName(self.context, 'portal_catalog')
    
    @property
    def isAnonymous(self):
        """True is user is anonymous False otherwise"""
        membertool = getToolByName(self.context, 'portal_membership')
        return membertool.isAnonymousUser()

    def getAbstractsByTopic(self, topic):
        """All abstracts for a given topic"""
        return self.catalog(portal_type="Abstract", 
                            Subject=topic,
                            sort_on="created",
                            )   # XXX maybe add a path constraint?

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
