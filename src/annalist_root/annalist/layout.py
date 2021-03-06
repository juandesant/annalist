"""
Annalist directory/site layout
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2014-2016, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import os.path

import logging
log = logging.getLogger(__name__)

# Annalist configuration and metadata files
#
# Directory layout:
#
#   $BASE_DATA_DIR
#     annalist-site/
#       c/
#         _annalist-site/
#           _annalist_collection/
#             coll_meta.json_ld
#             coll_prov.json_ld
#             coll_context.json_ld
#             _type/
#              :
#         <collection-id>/
#           _annalist_collection/
#             coll_meta.jsonld
#             coll_prov.jsonld
#             _type/
#               <type-id>/
#                 type_meta.jsonld
#                 type_prov.jsonld
#                :
#             _view/
#               <view-id>/
#                 view_meta.jsonld
#                 view_prov.jsonld
#                :
#             _list/
#               <list-id>/
#                 list_meta.jsonld
#                 list_prov.jsonld
#                :
#             (etc.)
#           d/
#             <type-id>/
#               <entity-id>/
#                 entity-data.jsonld
#                 entity-prov.jsonld
#                :
#              :
#         <collection-id>/
#          :

SITE_TYPEID             = "_site"
SITE_DIR                = "annalist_site"
SITEDATA_ID             = "_annalist_site"
BIBDATA_ID              = "Bibliography_defs"
SITEDATA_DIR            = "c/%(id)s"%{'id': SITEDATA_ID}
SITEDATA_OLD_DIR        = "_annalist_site"
SITE_META_PATH          = ""
SITE_META_FILE          = "@@unused@@site_meta.jsonld"
META_SITE_REF           = "@@unused@@./"
SITE_COLL_VIEW          = "c/%(id)s/"
SITE_COLL_PATH          = "c/%(id)s"
SITE_COLL_META_REF      = "c/%(id)s/_annalist_collection/"          # Used for testing
SITE_CONTEXT_FILE       = "site_context.jsonld"                     # Unused?

COLL_TYPEID             = "_coll"
COLL_META_DIR           = "_annalist_collection"
COLL_META_FILE          = "coll_meta.jsonld"
COLL_PROV_FILE          = "coll_prov.jsonld"
COLL_META_REF           = COLL_META_DIR + "/" + COLL_META_FILE
COLL_PROV_REF           = COLL_META_DIR + "/" + COLL_PROV_FILE
COLL_BASE_REF           = "d/"
META_COLL_REF           = "../"
META_COLL_BASE_REF      = "../d/"
COLL_CONTEXT_FILE       = "coll_context.jsonld"

#SITEDATA_TYPEID         = "_sitedata"                              # not used
SITEDATA_META_DIR       = SITEDATA_DIR + "/" + COLL_META_DIR        # used in tests
SITEDATA_META_FILE      = COLL_META_FILE                            # used in views
SITEDATA_PROV_FILE      = COLL_PROV_FILE                            # used in views
SITEDATA_CONTEXT_PATH   = "./"                                      # used in models

# -------------------------
# Entities of various types
# -------------------------
#
# NOTE: definitive entity URIs are *without* trailing "/".
#       Rediretion to a URI wit the trailing "/" retrieves a representation of the entity,
#       geberally an HTML form view.  Redirection to other forms is used for alternative
#       representations.
#

# Type records
TYPE_TYPEID             = "_type"                           # type id, used in URL
TYPE_DIR                = "_type"                           # collection directory in file system
TYPE_DIR_PREV           = "types"                           # collection directory in file system
TYPE_META_FILE          = "type_meta.jsonld"                # type metadata file name
TYPE_PROV_FILE          = "type_prov.jsonld"                # type provenance file name
COLL_BASE_TYPE_REF      = TYPE_TYPEID + "/%(id)s"           # ref type relative to collection base URL
COLL_TYPE_VIEW          = "d/" + COLL_BASE_TYPE_REF + "/"   # ref type view relative to collection entity
COLL_TYPE_PATH          = COLL_META_DIR + "/" + TYPE_DIR + "/%(id)s"
                                                            # type dir relative to collection root dir

# List description records
LIST_TYPEID             = "_list"                           # list id, used in URL
LIST_DIR                = "_list"                           # collection directory in file system
LIST_DIR_PREV           = "lists"                           # collection directory in file system
LIST_META_FILE          = "list_meta.jsonld"                # list metadata file name
LIST_PROV_FILE          = "list_prov.jsonld"                # list provenance file name
COLL_BASE_LIST_REF      = LIST_TYPEID + "/%(id)s"           # ref list relative to collection base URL
COLL_LIST_VIEW          = "d/" + COLL_BASE_LIST_REF + "/"   # ref list view relative to collection entity
COLL_LIST_PATH          = COLL_META_DIR + "/" + LIST_DIR + "/%(id)s"
                                                            # list dir relative to collection root dir

# View description records
VIEW_TYPEID             = "_view"                           # type id, used in URL
VIEW_DIR                = "_view"                           # collection directory in file system
VIEW_DIR_PREV           = "views"                           # previous collection directory
VIEW_META_FILE          = "view_meta.jsonld"                # view metadata file name
VIEW_PROV_FILE          = "view_prov.jsonld"                # view provenance file name
COLL_BASE_VIEW_REF      = VIEW_TYPEID + "/%(id)s"           # ref view relative to collection base URL
COLL_VIEW_VIEW          = "d/" + COLL_BASE_VIEW_REF + "/"   # ref view relative to collection entity
COLL_VIEW_PATH          = COLL_META_DIR + "/" + VIEW_DIR + "/%(id)s"
                                                            # view dir relative to collection root dir

# Field-group description records
GROUP_TYPEID            = "_group"                          # group id, used in URL
GROUP_DIR               = "_group"                          # collection directory in file system
GROUP_DIR_PREV          = "groups"                          # previous collection directory
GROUP_META_FILE         = "group_meta.jsonld"               # group metadata file name
GROUP_PROV_FILE         = "group_prov.jsonld"               # group provenance file name
COLL_BASE_GROUP_REF     = GROUP_TYPEID + "/%(id)s"          # ref group relative to collection base URL
COLL_GROUP_VIEW         = "d/" + COLL_BASE_GROUP_REF + "/"  # ref group view relative to collection entity
COLL_GROUP_PATH         = COLL_META_DIR + "/" + GROUP_DIR + "/%(id)s"
                                                            # group dir relative to collection root dir

# Field description records
FIELD_TYPEID            = "_field"                          # field id, used in URL
FIELD_DIR               = "_field"                          # collection directory in file system
FIELD_DIR_PREV          = "fields"                          # previous collection directory
FIELD_META_FILE         = "field_meta.jsonld"               # field metadata file name
FIELD_PROV_FILE         = "field_prov.jsonld"               # field provenance file name
COLL_BASE_FIELD_REF     = FIELD_TYPEID + "/%(id)s"          # ref field relative to collection base URL
COLL_FIELD_VIEW         = "d/" + COLL_BASE_FIELD_REF + "/"  # ref field view relative to collection entity
COLL_FIELD_PATH         = COLL_META_DIR + "/" + FIELD_DIR + "/%(id)s"
                                                            # field dir relative to collection root dir

# User permission records
USER_TYPEID             = "_user"                           # type id, used in URL
USER_DIR                = "_user"                           # collection directory in file system
USER_DIR_PREV           = "users"                           # previous collection directory
USER_META_FILE          = "user_meta.jsonld"                # user metadata file name
USER_PROV_FILE          = "user_prov.jsonld"                # user provenance file name
COLL_BASE_USER_REF      = USER_TYPEID + "/%(id)s"           # ref user relative to collection base URL
COLL_USER_VIEW          = "d/" + COLL_BASE_USER_REF + "/"   # ref user relative to collection entity
COLL_USER_PATH          = COLL_META_DIR + "/" + USER_DIR + "/%(id)s"
                                                            # user dir relative to collection root dir

# Vocabulary namespace records
VOCAB_TYPEID            = "_vocab"                          # vocab id, used in URL
VOCAB_DIR               = "_vocab"                          # collection directory in file system
VOCAB_DIR_PREV          = "vocabs"                          # previous collection directory
VOCAB_META_FILE         = "vocab_meta.jsonld"               # vocab metadata file name
VOCAB_PROV_FILE         = "vocab_prov.jsonld"               # vocab provenance file name
COLL_BASE_VOCAB_REF     = VOCAB_TYPEID + "/%(id)s"          # ref vocab relative to collection base URL
COLL_VOCAB_VIEW         = "d/" + COLL_BASE_VOCAB_REF + "/"  # ref vocab view relative to collection entity
COLL_VOCAB_PATH         = COLL_META_DIR + "/" + VOCAB_DIR + "/%(id)s"
                                                            # vocab dir relative to collection root dir

# Enumerated value description records
ENUM_TYPEID             = "_enum"                           # enum id, used in URL
ENUM_DIR                = "_enum"                           # collection directory in file system
ENUM_DIR_PREV           = "enums"                           # previous collection directory
ENUM_META_FILE          = "enum_meta.jsonld"                # enum metadata file name
ENUM_PROV_FILE          = "enum_prov.jsonld"                # enum provenance file name
ENUM_COLL_BASE_REF      = "../../../"                       # Ref collection base from enum, overides EntityData
ENUM_CONTEXT_FILE       = ENUM_COLL_BASE_REF + COLL_CONTEXT_FILE  # ref collection context file
COLL_BASE_ENUM_REF      = "%(type_id)s/%(id)s"              # ref enum relative to collection base URL
COLL_ENUM_VIEW          = "d/%(type_id)s/%(id)s/"           # ref enum view relative to collection entity
COLL_ENUM_PATH          = COLL_META_DIR + "/" + ENUM_DIR + "/%(type_id)s/%(id)s"

# Record type data records (these act as parents for Entity data records)
TYPEDATA_TYPEID         = "_entitytypedata"                 # typedata id
TYPEDATA_META_FILE      = "type_data_meta.jsonld"           # type data metadata file name
TYPEDATA_PROV_FILE      = "type_data_prov.jsonld"           # type data provenance file name
COLL_BASE_TYPEDATA_REF  = "%(id)s"                          # ref type data relative to collection base URL
TYPEDATA_COLL_BASE_REF  = "../"                             # ref collection base from record type data
TYPEDATA_CONTEXT_FILE   = TYPEDATA_COLL_BASE_REF + COLL_CONTEXT_FILE  # ref collection context file
COLL_TYPEDATA_VIEW      = "d/%(id)s/"                       # ref type data view relative to collection entity
COLL_TYPEDATA_PATH      = "d/%(id)s"                        # dir type data relative to collection root dir

# Entity data records (these contain user data, organized by record type)
# Entity data layout information...
COLL_ENTITYDATA_PATH    = "d/"
TYPEDATA_ENTITY_VIEW    = "%(id)s/"
TYPEDATA_ENTITY_PATH    = "%(id)s"
COLL_ENTITY_VIEW        = "d/%(type_id)s/%(id)s/"
COLL_ENTITY_PATH        = "d/%(type_id)s/%(id)s"
SITE_ENTITY_VIEW        = "c/%(coll_id)s/d/%(type_id)s/%(id)s/"
SITE_ENTITY_PATH        = "c/%(coll_id)s/d/%(type_id)s/%(id)s"
ENTITY_DATA_FILE        = "entity_data.jsonld"
ENTITY_PROV_FILE        = "entity_prov.jsonld"
ENTITY_LIST_FILE        = "entity_list.jsonld"  # Entity list as JSON resource
COLL_BASE_ENTITY_REF    = "%(type_id)s/%(id)s"
ENTITY_COLL_BASE_REF    = "../../"
#@@ NOTE: @base ignored when loading external context - is this correct?
#@@ ENTITY_CONTEXT_FILE     = COLL_CONTEXT_FILE
ENTITY_CONTEXT_FILE     = ENTITY_COLL_BASE_REF + COLL_CONTEXT_FILE
ENTITY_OLD_DATA_FILE    = "entity-data.jsonld"

# Other symbols
TASK_TYPEID             = "_task"               # task id

# Lists of directory names for collection migration, etc:
DATA_DIRS_CURR_PREV = (
    [ (TYPE_DIR,  TYPE_DIR_PREV)
    , (LIST_DIR,  LIST_DIR_PREV)
    , (VIEW_DIR,  VIEW_DIR_PREV)
    , (GROUP_DIR, GROUP_DIR_PREV)
    , (FIELD_DIR, FIELD_DIR_PREV)
    , (ENUM_DIR,  ENUM_DIR_PREV)
    ])
DATA_DIRS       = map(lambda pair:pair[0], DATA_DIRS_CURR_PREV)
DATA_DIRS_PREV  = map(lambda pair:pair[1], DATA_DIRS_CURR_PREV)
DATA_VOCAB_DIRS = DATA_DIRS + [VOCAB_DIR]

COLL_DIRS_CURR_PREV = (
    DATA_DIRS_CURR_PREV +
    [ (USER_DIR,  USER_DIR_PREV)
    , (VOCAB_DIR, VOCAB_DIR_PREV)
    ])
COLL_DIRS       = map(lambda pair:pair[0], COLL_DIRS_CURR_PREV)
COLL_DIRS_PREV  = map(lambda pair:pair[1], COLL_DIRS_CURR_PREV)

# Name generation suffixes for tasks that generate new records
SUFFIX_LIST             = ""
SUFFIX_VIEW             = ""
SUFFIX_TYPE             = ""
SUFFIX_REPEAT           = "_r"
SUFFIX_REPEAT_P         = "_r"
SUFFIX_REPEAT_G         = "_r"
SUFFIX_MULTI            = "_m"
SUFFIX_MULTI_P          = "_m"
SUFFIX_MULTI_G          = "_m"

class Layout(object):
    """
    A dynamically created layout value with paths that are dynamically constructed 
    using a supplied base directory.
    """

    def __init__(self, base_data_dir):
        """
        Dynamically initialize a layout value
        """
        self.BASE_DIR           = base_data_dir
        self.SITE_DIR           = SITE_DIR
        self.SITEDATA_ID        = SITEDATA_ID
        self.SITEDATA_DIR       = SITEDATA_DIR
        self.SITEDATA_OLD_DIR   = SITEDATA_OLD_DIR
        self.SITEDATA_META_DIR  = SITEDATA_META_DIR                         # e.g. c/_annalist_site/_annalist_collection
        self.SITE_PATH          = os.path.join(base_data_dir, SITE_DIR)     # e.g. /data/annalist_site
        self.SITEDATA_CONTEXT_DIR = os.path.join(                          # e.g. /data/annalist_site/c/_annalist_site/_annalist_collection/site_context.jsonld
            base_data_dir, SITE_DIR, SITEDATA_META_DIR, COLL_CONTEXT_FILE
            ) 
        return

# End.
