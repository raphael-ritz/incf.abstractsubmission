# Inspired by
# http://opensourcehacker.com/2013/01/04/exporting-plone-content-as-json/
# Thanks Mikko!

import os
import base64

try:
    import json
except ImportError:
    # Python 2.54 / Plone 3.3 use simplejson
    # version > 2.3 < 3.0
    import simplejson as json

from Products.Five.browser import BrowserView
from Products.CMFCore.interfaces import IFolderish
from DateTime import DateTime

#: Private attributes we add to the export list
EXPORT_ATTRIBUTES = ["portal_type", "id"]

#: Do we dump out binary data... default we do, but can be controlled with env var
EXPORT_BINARY = os.getenv("EXPORT_BINARY", None)
if EXPORT_BINARY:
    EXPORT_BINARY = EXPORT_BINARY == "true"
else:
    EXPORT_BINARY = False

class JSONView(BrowserView):
    """Present Archetypes-based content as JSON"""

    def convert(self, value):
        """
        Convert value to more JSON friendly format.
        """
        if isinstance(value, DateTime):
            # Zope DateTime
            # http://pypi.python.org/pypi/DateTime/3.0.2
            return value.ISO8601()
        elif hasattr(value, "isBinary") and value.isBinary():

            if not EXPORT_BINARY:
                return None

            # Archetypes FileField and ImageField payloads
            # are binary as OFS.Image.File object
            data = getattr(value.data, "data", None)
            if not data:
                return None
            return base64.b64encode(data)
        else:
            # Passthrough
            return value

    def fieldData(self, context):
        data = {}
        for field in context.Schema().viewableFields(context):
            name = field.getName()
            value = field.getRaw(context)
            data[name] = self.convert(value)
        return data

    def attributeData(self, context):
        data = {}
        for key in EXPORT_ATTRIBUTES:
            data[key] = self.convert(getattr(context, key, None))
        return data

    def export(self, context):
        """Export fields and selected attributes"""

        data = self.fieldData(context)
        data.update(self.attributeData(context))

        return [data]

    def json_view(self):
        """AT-based content as JSON"""

        context = self.context.aq_inner
        data = self.export(context)
        pretty = json.dumps(data, sort_keys=True, indent=4)
        self.request.response.setHeader("Content-type", "application/json")
        return pretty
