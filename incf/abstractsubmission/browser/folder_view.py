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

    def getAbstractsByTopic(self, topic, sort_on="created", **kw):
        """All abstracts for a given topic"""
        return self.catalog(portal_type="Abstract", 
                            Subject=topic,
                            sort_on=sort_on,
                            **kw
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

    def abstractsWithImages(self, url = None):
        """List of identifiers for all contributions that have an
        image included and that are accepted or published

        Sorted on Identifier

        If 'url' is not None the absolute URL to the abstract will
        be included
        """
        result = []
        brains = self.catalog(portal_type='Abstract',
                              review_state=['accepted', 'published'],
                              sort_on='getIdentifier',
                              )
        for brain in brains:
            obj = brain.getObject()
            if not obj.hasImage():
                continue
            if url is not None:
                s = "%s %s" % (obj.getIdentifier(), obj.absolute_url())
            else:
                s = obj.getIdentifier()

            result.append(s)
            
        return '\n\r'.join(result)
        

        
    # plain text export for the abstract book
    
    def abstractBookSource(self, separator='\r\n\r\n'):
        """Malin and Helena will take it from here"""

        out = StringIO()
        abstracts = []
        topics = self.context.getTopics()
        for topic in topics:
            abstracts.extend(self.getAbstractsByTopic(topic, 'getIdentifier'))

        for abstract in abstracts:
            if abstract.review_state not in ['accepted', 'published']:
                continue
            abstract = abstract.getObject()
            out.write(abstract.abstractBookSource())
            out.write(separator)
            
        value = out.getvalue()
        out.close()
        return value

    # support the various indexes

    def authorIndex(self, rft=None):
        """Author followed by comma separated list of abstract ids;
        one per line sorted on last name"""

        data = {}
        contributions = self.catalog(portal_type=['Abstract', 'Speaker'])
        for abstract in contributions:
            if abstract.review_state not in ['accepted', 'published']:
                continue
            obj = abstract.getObject()
            authors = obj.getAuthors()
            id = obj.getIdentifier()
            for author in authors:
                a = "%(lastname)s, %(firstnames)s" % author
                a = a.strip()
                if a.endswith('.'):
                    a = a[:-1]
                try: 
                    value = data[a]
                except KeyError:
                    value = []
                value.append(id)
                data[a] = value

        result = StringIO()
        keys = data.keys()
        keys.sort()
        for k in keys:
            ids = data[k]
            ids.sort()
            if rft is None:
                result.write('%s\t%s\r\n' % (k, ', '.join(ids)))
            else:
                result.write('%s**(rft)**%s\r\n' % (k, ', '.join(ids)))
        value = result.getvalue()
        result.close()
        return value

    def sessionIndex(self, separator='\r\n'):
        """Contributions groups by session and sorted by id within"""

        # XXX how would one get the order if sessions are just taken from the
        # catalog as well?
        sessions = ['Keynote',
                    'Workshop 1',
                    'Workshop 2',
                    'Workshop 3',
                    'Workshop 4',
                    'Demo Session',
                    'Poster Session 1',
                    'Poster Session 2',
                    ]

        data = []

        for session in sessions:
            data.append(separator + session + separator)
            abstracts = self.catalog(portal_type=['Abstract','Speaker'],
                                     review_state=['accepted', 'published'],
                                     getSessionType=session,
                                     sort_on='getIdentifier',
                                     )
            for abstract in abstracts:
                authors = abstract.getObject().getAuthors()
                id = abstract.getObject().getIdentifier()
                authorinfo = authors[0]
                authorinfo['id'] = id
                data.append("%(id)s %(lastname)s, %(firstnames)s" % authorinfo)

        return separator.join(data)

    def topicIndex(self, separator='\r\n'):
        """Contributions grouped by category"""

        topics = self.context.getTopics()
        data = []
        
        for topic in topics:
            data.append(separator + topic + separator)
            abstracts = self.getAbstractsByTopic(topic,
                                                 sort_on='getIdentifier',
                                                 review_state=['accepted', 'published'],
                                                 )
            for abstract in abstracts:
                authors = abstract.getObject().getAuthors()
                id = abstract.getObject().getIdentifier()
                authorinfo = authors[0]
                authorinfo['id'] = id
                data.append("%(id)s %(lastname)s, %(firstnames)s" % authorinfo)

        return separator.join(data)
