import random
import transaction

from Products.Five.browser import BrowserView

from incf.abstractsubmission.sampledata import ABSTRACTS
 

class Upload(BrowserView):
    """Support uploading of sample data"""

    def upload(self):
        """Upload sample data"""
        
        target = self.context
        ids = target.contentIds()

        for abstract in ABSTRACTS:
            id = abstract.get('id', '')
            if not id or id in ids:
                continue
            target.invokeFactory(type_name="Abstract",
                                 id=id,
                                 )
            target[id].edit(**abstract)
            target[id].reindexObject()

        # to fully populate repeat the above but with
        # random permutations of autors and random
        # choice of topic

        topics = target.getTopics()

        for i in range(40):
            ids = target.contentIds()
            for abs in ABSTRACTS:
                # work on copies - we are going to change it
                abstract = abs.copy()
                id = abstract.get('id', '')
                if id is '':
                    continue
                id = '%s-%d' % (id, i+1)
                abstract['id'] = id   # write back to avoid renaming later
                abstract['topic'] = random.choice(topics)
                authors = abstract['authors']
                random.shuffle(authors)
                abstract['authors'] = authors            
                if id in ids:
                    print "Found %s - doing nothing" % id
                    continue
                print "Creating %s" % id
                target.invokeFactory(type_name="Abstract",
                                     id=id,
                                     )
                target[id].edit(**abstract)
                target[id].reindexObject()
            transaction.savepoint(optimistic=True)
