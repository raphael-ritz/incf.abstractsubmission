from StringIO import StringIO
from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName
from contentratings.interfaces import IUserRating

TEMPLATE = '"%s"'

# (id, label)
supported_fields = [('identifier', 'Identifier'),
                    ('state', 'Review state'),
                    ('created', 'Creation date and time'),
                    ('modified', 'Last modification date and time'),
                    ('firstnames', 'First author: First name(s)'),
                    ('lastname', 'First author: Last name'),
                    ('email', 'First author: Email'),
                    ('affiliation', 'First author: Affiliation'),
                    ('country', 'First author: Country'),
                    ('authors', 'Full author list including affiliations'),
                    ('abstract_title', 'Abstract title'),
                    ('body', 'Main text of abstract'),
                    ('acknowledgments', 'Acknowledgments'),
                    ('references', 'References'),
                    ('imagetag', 'Image tag'),
                    ('caption', 'Image caption'),
                    ('format', 'Presentation format'),
                    ('topic', 'Topic'),
                    ('session', 'Session'),
                    ('url', 'Abstract URL'),
                    ('rating', 'Cummulative rating'),
                    ('#replies', 'Number of comments'),
                    ('comments', 'Comments (concatenated)'),
                    ]

def getIdentifier(abstract):
    return abstract.getIdentifier() or ''

def getState(abstract):
    wft = getToolByName(abstract, 'portal_workflow')
    return wft.getInfoFor(abstract, 'review_state')

def getCreated(abstract):
    return abstract.created().strftime('%Y-%m-%d %H:%M')

def getModified(abstract):
    return abstract.modified().strftime('%Y-%m-%d %H:%M')
                    
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

def getAuthors(abstract):
    return abstract.formatAuthors() or ''

def getTitle(abstract):
    return abstract.Title() or ''

def getBody(abstract):
    return abstract.getPlainText() or ''

def getAcknowledgments(abstract):
    return abstract.getAcknowledgments(mimetype="text/plain") or ''

def getReferences(abstract):
    return abstract.getCitations(mimetype="text/plain") or ''

def getImageTag(abstract):
    return abstract.tag() or ''

def getCaption(abstract):
    return abstract.getImageCaption() or ''

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
    'identifier': getIdentifier,
    'state': getState,
    'created': getCreated,
    'modified': getModified,
    'firstnames': getFirstName,
    'lastname': getLastName,
    'email': getEmail,
    'affiliation': getAffiliation,
    'country': getCountry,
    'authors': getAuthors,
    'abstract_title': getTitle,
    'body': getBody,
    'acknowledgments': getAcknowledgments,
    'references': getReferences,
    'imagetag': getImageTag,
    'caption': getCaption,
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

    def csv_export(self,
                   states=None,
                   fields=None,
                   filename='abstracts.csv',
                   delimiter=',',
                   newline='\r\n',
                   ):
        """Main method to be called for the csv export"""
        
        if fields is None:
            fields = [field[0] for field in supported_fields]
            
        wft = getToolByName(self.context, 'portal_workflow')

        out = StringIO()
        out.write(delimiter.join(fields) + newline)
            
        for abstract in self.context.contentValues():
            review_state = wft.getInfoFor(abstract, 'review_state')
            if states and review_state not in states:
                continue
            values = []
            for field in fields:
                raw = accessors[field](abstract)
                raw = raw.replace('"', '""')
                value = TEMPLATE % raw
                values.append(value)
            out.write(delimiter.join(values) + newline)
            
        value = out.getvalue()
        out.close()
        self.request.RESPONSE.setHeader('Content-Type', 'application/x-msexcel')
        self.request.RESPONSE.setHeader("Content-Disposition", 
                                        "inline;filename=%s"%filename)

        return value

    def states_vocab(self):
        """Provide vocabulary for the state selection"""
        wft = getToolByName(self.context, 'portal_workflow')
        wf_id = wft.getChainForPortalType('Abstract')[0]
        wf = wft[wf_id]
        vocab = []
        for state in wf.states.values():
            vocab.append((state.getId(), state.title))
        return vocab

    def fields_vocab(self):
        """Vocabulary for the field selection"""
        return supported_fields

    def toggleSelection(self, states, fields):
        """Return a URL specified for bulk (de)selection of
        states or fields"""
        base = self.context.absolute_url()
        base = base + '/csv_export_form'
        arguments = []
        if states:
            arguments.append('states_selected=1')
        if fields:
            arguments.append('fields_selected=1')
        if not arguments:
            return base
        return base + '?' + '&'.join(arguments)
        

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

