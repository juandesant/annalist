"""
Analist site-related facilities
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2014, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import os
import os.path
import collections

import logging
log = logging.getLogger(__name__)

from django.conf import settings

from annalist.collection    import Collection
from annalist.views         import AnnalistGenericView
from annalist.layout        import Layout

dir_layout = Layout(settings.BASE_DATA_DIR)

class Site(object):

    def __init__(self, sitebaseuri, sitebasedir):
        """
        Initialize a Site object

        sitebaseuri     the base URI of the site
        sitebasedir     the base dictionary for site information
        """
        log.info("Site init: %s"%(sitebasedir))
        self._baseuri = sitebaseuri if sitebaseuri.endswith("/") else sitebaseuri+"/"
        self._basedir = sitebasedir if sitebasedir.endswith("/") else sitebasedir+"/"
        return

    def collections(self):
        """
        Generator enumerates and returns collection IDs that are part of a site.
        """
        site_files   = os.listdir(self._basedir)
        for f in site_files:
            p = os.path.join(self._basedir,f)
            if os.path.isdir(p):
                p2 = os.path.join(p, dir_layout.COLL_META_DIR)
                if os.path.isdir(p2):
                    yield f
        return

    def collections_dict(self):
        """
        Return a dictionary of collection URIs indexed by collledtion id
        """
        coll = collections.OrderedDict()
        for c in self.collections():
            coll[c] = { "uri": self._baseuri+c+"/", "dir": self._basedir+c+"/" }
        return coll

    def add_collection(self, coll_id, coll_meta):
        """
        Add a new collection to the current site

        coll_id     identifier for the new collection, as a string
                    with a form that is valid as URI path segment.
        coll_meta   a dictionary providing additional information about
                    the collection to be created.

        returns a Collection object for the newly created collection.
        """
        c = Collection.create(coll_id, coll_meta, self._baseuri, self._basedir)
        return c


class SiteView(AnnalistGenericView):
    """
    View class to handle requests to the annalist site home URI
    """
    def __init__(self):
        super(SiteView, self).__init__()
        return

    # GET

    def get(self, request):
        """
        Create a rendering of the current site home page, containing (among other things)
        a list of defined collections.
        """
        def resultdata():
            site = Site(self.get_request_uri(), dir_layout.SITE_PATH)
            return { "collections":  site.collections_dict() }
        return (
            self.authenticate() or 
            self.render_html(resultdata(), 'annalist_site.html') or 
            self.error(self.error406values())
            )

# End.