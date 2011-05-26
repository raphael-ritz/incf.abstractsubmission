from StringIO import StringIO
from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName
from contentratings.interfaces import IUserRating


class FolderView(BrowserView):
    """Various UI methods"""

    @property
    def catalog(self):
        return getToolByName(self.context, 'portal_catalog')

    @property
    def membertool(self):
        return getToolByName(self.context, 'portal_membership')
    
    @property
    def isAnonymous(self):
        """True if user is anonymous False otherwise"""
        return self.membertool.isAnonymousUser()

    def getAbstractsByTopic(self, topic, sort_on="created"):
        """All abstracts for a given topic"""
        return self.catalog(portal_type="Abstract", 
                            Subject=topic,
                            sort_on=sort_on,
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
        userid = self.membertool._getSafeMemberId()
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

    def showRating(self):
        """Review portal content is needed to see the rating"""
        return self.membertool.checkPermission('Review portal content', self.context)

    def rating(self, abstract_brain):
        """Return an HTML snippet including the formated rating"""
        abstract = abstract_brain.getObject()
        rated = IUserRating(abstract)
        average = float(rated.averageRating)
        number = rated.numberOfRatings
        if number == 0:
            rating = "(<span class='not-rated'>not rated</span>)"
        else:
            rating = "(<span class='rating-%d'>%2.2f (%s)</span>)" % (round(average), average, number)
        return rating

    def notified(self, abstract_brain):
        """Return an HTML snippet including the notification info"""
        abstract = abstract_brain.getObject()
        notified = abstract.notified()
        if notified is None:
            return "(No notification send)"
        return "(notified: %s)" % notified

        
    # plain text export for the abstract book
    
    def abstractBookSource(self, separator='\n\n'):
        """Malin and Helena will take it from here"""

        out = StringIO()
        abstracts = []
        topics = self.context.getTopics()
        for topic in topics:
            abstracts.extend(self.getAbstractsByTopic(topic, 'getIdentifier'))

        for abstract in abstracts:
            abstract = abstract.getObject()
            out.write(abstract.abstractBookSource())
            out.write(separator)
            
        value = out.getvalue()
        out.close()
        return value
        
