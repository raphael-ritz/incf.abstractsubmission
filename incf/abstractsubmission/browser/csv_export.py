from StringIO import StringIO
from Products.Five.browser import BrowserView
from contentratings.interfaces import IUserRating

TEMPLATE = '"%s"'

supported_fields = ['firstnames',
                    'lastname',
                    'email',
                    'affiliation',
                    'country',
                    'title',
                    'format',
                    'topic',
                    'session',
                    'url',
                    'rating',
                    '#replies',
                    'comments',
                    ]

def getFirstName(abstract):
    return abstract.getAuthors()[0].get('firstnames') or ''

def getLastName(abstract):
    return abstract.getAuthors()[0].get('lastname') or ''

def getEmail(abstract):
    return abstract.getAuthors()[0].get('email') or ''

def getAffiliation(abstract):
    return abstract.getAuthors()[0].get('affiliation') or ''

def getCountry(abstract):
    return abstract.Country() or ''

def getTitle(abstract):
    return abstract.Title() or ''

def getPresentationFormat(abstract):
    return abstract.getPresentationFormat() or ''

def getTopic(abstract):
    return abstract.getTopic() or ''

def getSession(abstract):
    return ', '.join(abstract.getSessionType())

def getUrl(abstract):
    return abstract.absolute_url()

def getRating(abstract):
    rated = IUserRating(abstract)
    average = float(rated.averageRating)
    number = rated.numberOfRatings
    return "%2.2f (%s)" % (average, number)
    
def getReplyCount(abstract):
    return str(comment_data(abstract)[0])

def getComments(abstract):
    return comment_data(abstract)[1]


accessors = {
    'firstnames': getFirstName,
    'lastname': getLastName,
    'email': getEmail,
    'affiliation': getAffiliation,
    'country': getCountry,
    'title': getTitle,
    'format': getPresentationFormat,
    'topic': getTopic,
    'session': getSession,
    'url': getUrl,
    'rating': getRating,
    '#replies': getReplyCount,
    'comments': getComments,
    }


class CSVExport(BrowserView):
    """Methods for the CSV export of a submission folder"""

    def csv_export(self, fields=[], delimiter=',', newline='\r\n'):
        """Main method to be called for the csv export"""
        
        if not fields:
            fields = supported_fields
        out = StringIO()
        out.write(delimiter.join(fields) + newline)

        for abstract in self.context.contentValues():
            values = []
            for field in fields:
                value = TEMPLATE % accessors[field](abstract)
                values.append(value)
            out.write(delimiter.join(values) + newline)
            
        value = out.getvalue()
        out.close()
        self.request.RESPONSE.setHeader('Content-Type', 'application/x-msexcel')
        self.request.RESPONSE.setHeader("Content-Disposition", 
                                        "inline;filename=abstracts.csv")

        return value


def comment_data(abstract):
    """Helper function returning the number and concatenated text
    of comments made on 'abstract'"""
    # try old API first
    try:
        reply_count = abstract.portal_discussion.getDiscussionFor(abstract).replyCount(abstract)
        replies = abstract.portal_discussion.getDiscussionFor(abstract).getReplies()
        if not replies:
            return 0, 'None'
        comments = []
        for r in replies:
            comments.append("%s (%s): %s - %s" % (r.Creator(),
                                                   r.created().Date(),
                                                   r.Title(),
                                                   r.CookedBody()))
        comments = " -- ".join(comments)
        return reply_count, comments
    except AttributeError:
        # usually happens if plone.app.discussion is used
        # then the following should work
        from plone.app.discussion.interfaces import IConversation
        conversation = IConversation(abstract)
        reply_count = len(conversation.objectIds())
        if not reply_count:
            return 0, 'None'        
        replies = [conversation[id] for id in conversation.objectIds()]
        comments = []
        for r in replies:
            comments.append("%s (%s): %s" % (r.author_name,
                                              r.modification_date.strftime('%Y-%m-%d %H:%M'),
                                              r.text))
        comments = " -- ".join(comments)
        return reply_count, comments.encode('utf-8')            

