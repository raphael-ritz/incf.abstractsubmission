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

