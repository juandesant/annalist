"""
Annalist data record for a member of an enumerated type
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2014, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import os
import os.path
import urlparse
import shutil

import logging
log = logging.getLogger(__name__)

from django.conf import settings

from annalist                   import layout
from annalist.exceptions        import Annalist_Error
from annalist.identifiers       import ANNAL
from annalist                   import util
from annalist.models.entity     import Entity
from annalist.models.entitydata import EntityData

class RecordEnumBase(EntityData):

    _entitytype     = ANNAL.CURIE.Enum
    _entitytypeid   = "_enum"
    _entityview     = layout.COLL_ENUM_VIEW
    _entitypath     = layout.COLL_ENUM_PATH
    _entityfile     = layout.ENUM_META_FILE
    _entityprov     = layout.ENUM_PROV_FILE
    _baseref        = layout.ENUM_COLL_BASE_REF      # Override EntityData..
    _contextref     = layout.ENUM_CONTEXT_FILE

    def __init__(self, parent, entity_id, type_id):
        self._entitytypeid = type_id
        super(RecordEnumBase, self).__init__(parent, entity_id)
        return

    def _migrate_filenames(self):
        """
        Override EntityData method
        """
        return None

def RecordEnumFactory(name, type_id):
    """
    Returns a dynamically-subclassed instance of RecordEnumBase using the supplied 
    class name and type_id for all created instances.
    """
    def RecordEnumInit(self, parent, entity_id):
        super(RecordEnumBase, self).__init__(parent, entity_id)
        return
    return type(name, (RecordEnumBase,), 
        { '_entitytypeid':  type_id
        , '_entitypath':    layout.COLL_ENUM_PATH%{'id': "%(id)s", 'type_id': type_id}
        , '__init__': RecordEnumInit}
        )

# End.
