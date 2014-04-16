"""
Utility functions to support entity data testing
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2014, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import os
import urlparse

import logging
log = logging.getLogger(__name__)

from django.conf                    import settings
from django.http                    import QueryDict
from django.utils.http              import urlquote, urlunquote
from django.core.urlresolvers       import resolve, reverse

from annalist.util                  import valid_id
from annalist.identifiers           import RDF, RDFS, ANNAL
from annalist                       import layout
from annalist.fields.render_utils   import get_placement_classes

from entity_testutils               import (
    collection_dir, 
    collection_edit_uri,
    site_title
    )

from tests  import TestHost, TestHostUri, TestBasePath, TestBaseUri, TestBaseDir

#   -----------------------------------------------------------------------------
#
#   Directory generating functions
#
#   -----------------------------------------------------------------------------

# Each entity type has its own data directory within a collection:

def recorddata_dir(coll_id="testcoll", type_id="testtype"):
    return collection_dir(coll_id) + layout.COLL_TYPEDATA_PATH%{'id': type_id} + "/"

def entitydata_dir(coll_id="testcoll", type_id="testtype", entity_id="testentity"):
    return recorddata_dir(coll_id, type_id) + layout.TYPEDATA_ENTITY_PATH%{'id': entity_id} + "/"


#   -----------------------------------------------------------------------------
#
#   URI generating functions
#
#   -----------------------------------------------------------------------------

#   These all use the Django `reverse` function so they correspond to
#   the declared URI patterns.

def entity_uri(coll_id="testcoll", type_id="testtype", entity_id="entity_id"):
    viewname = "AnnalistEntityDefaultDataView"
    kwargs   = {'coll_id': coll_id, 'type_id': type_id, 'entity_id': entity_id}
    return reverse(viewname, kwargs=kwargs)

def entitydata_edit_uri(action, coll_id, type_id=None, entity_id=None, view_id=None):
    if view_id:
        viewname = ( 
            'AnnalistEntityNewView'             if action == "new" else
            'AnnalistEntityEditView'
            )
        kwargs = {'action': action, 'coll_id': coll_id, 'view_id': view_id}
    else:
        viewname = ( 
            'AnnalistEntityDefaultNewView'      if action == "new" else
            'AnnalistEntityDefaultEditView'
            )
        kwargs = {'action': action, 'coll_id': coll_id}
    if type_id:
        kwargs.update({'type_id': type_id})
    if entity_id:
        kwargs.update({'entity_id': entity_id})
    return reverse(viewname, kwargs=kwargs)

def entitydata_list_all_uri(coll_id="testcoll", list_id=None):
    if list_id:
        viewname = "AnnalistEntityGenericList"
        kwargs   = {'list_id': list_id, 'coll_id': coll_id}
    else:
        viewname = "AnnalistEntityDefaultListAll"
        kwargs   = {'coll_id': coll_id}
    return reverse(viewname, kwargs=kwargs)

def entitydata_list_type_uri(coll_id="testcoll", type_id="testtype", list_id=None):
    if list_id:
        viewname = "AnnalistEntityGenericList"
        kwargs   = {'list_id': list_id, 'coll_id': coll_id, 'type_id': type_id}
    else:
        viewname = "AnnalistEntityDefaultListType"
        kwargs   = {'coll_id': coll_id, 'type_id': type_id}
    return reverse(viewname, kwargs=kwargs)

def entitydata_delete_confirm_uri(coll_id, type_id):
    kwargs = {'coll_id': coll_id, 'type_id': type_id}
    return reverse("AnnalistEntityDataDeleteView", kwargs=kwargs)

#   -----------------------------------------------------------------------------
#
#   ----- Entity data
#
#   -----------------------------------------------------------------------------

#   The following all return some arbitrary entity data, but corresponding to 
#   the same entity at different stages of the processing (initial values, 
#   stored values, Django view context data and Django form data).

def entitydata_value_keys():
    """
    Keys in default view entity data
    """
    return (
        [ 'annal:id', 'annal:type'
        , 'annal:uri', 'annal:urihost', 'annal:uripath'
        , 'rdfs:label', 'rdfs:comment'
        ])

def entitydata_create_values(entity_id, type_id="testtype", update="Entity"):
    """
    Data used when creating entity test data
    """
    return (
        { 'rdfs:label': '%s testcoll/%s/%s'%(update, type_id, entity_id)
        , 'rdfs:comment': '%s coll testcoll, type %s, entity %s'%(update, type_id, entity_id)
        })

def entitydata_values(entity_id, update="Entity", coll_id="testcoll", type_id="testtype", hosturi=TestHostUri):
    d = entitydata_create_values(entity_id, type_id=type_id, update=update).copy()
    d.update(
        { '@id':            './'
        , 'annal:id':       entity_id
        , 'annal:type':     'annal:EntityData'
        , 'annal:uri':      hosturi + entity_uri(coll_id, type_id, entity_id)
        , 'annal:urihost':  urlparse.urlparse(hosturi).netloc
        , 'annal:uripath':  entity_uri(coll_id, type_id, entity_id)
        })
    return d

def entitydata_context_data(
        entity_id=None, orig_id=None, type_id="testtype", type_ids=[],
        action=None, update="Entity"
    ):
    context_dict = (
        { 'title':              site_title()
        , 'coll_id':            'testcoll'
        , 'type_id':            'testtype'
        , 'orig_id':            'orig_entity_id'
        , 'fields':
          [ { 'field_label':        'Id'
            , 'field_id':           'Entity_id'
            , 'field_name':         'entity_id'
            , 'field_render_view':  'field/annalist_view_entityref.html'
            , 'field_render_edit':  'field/annalist_edit_text.html'
            , 'field_placement':    get_placement_classes('small:0,12;medium:0,6')
            , 'field_value_type':   'annal:Slug'
            # , 'field_value':      (Supplied separately)
            , 'options':            []
            }
          , { 'field_label':        'Type'
            , 'field_id':           'Entity_type'
            , 'field_name':         'entity_type'
            , 'field_render_view':  'field/annalist_view_select.html'
            , 'field_render_edit':  'field/annalist_edit_select.html'
            , 'field_placement':    get_placement_classes('small:0,12;medium:6,6right')
            , 'field_value_type':   'annal:Slug'
            # , 'field_value':      (Supplied separately)
            , 'options':            []
            }
          , { 'field_label':        'Label'
            , 'field_id':           'Entity_label'
            , 'field_name':         'Entity_label'
            , 'field_render_view':  'field/annalist_view_text.html'
            , 'field_render_edit':  'field/annalist_edit_text.html'
            , 'field_placement':    get_placement_classes('small:0,12')
            , 'field_value_type':   'annal:Text'
            , 'field_value':        '%s data ... (testcoll/testtype)'%(update)
            , 'options':            []
            }
          , { 'field_label':        'Comment'
            , 'field_id':           'Entity_comment'
            , 'field_name':         'Entity_comment'
            , 'field_render_view':  'field/annalist_view_textarea.html'
            , 'field_render_edit':  'field/annalist_edit_textarea.html'
            , 'field_placement':    get_placement_classes('small:0,12')
            , 'field_value_type':   'annal:Longtext'
            , 'field_value':        '%s description ... (testcoll/testtype)'%(update)
            , 'options':            []
            }
          ]
        , 'continuation_uri':   entitydata_list_type_uri("testcoll", type_id)
        })
    if entity_id:
        context_dict['fields'][0]['field_value'] = entity_id
        context_dict['fields'][1]['field_value'] = type_id if valid_id(type_id) else None
        context_dict['fields'][2]['field_value'] = '%s testcoll/testtype/%s'%(update,entity_id)
        context_dict['fields'][3]['field_value'] = '%s coll testcoll, type testtype, entity %s'%(update,entity_id)
        context_dict['orig_id']     = entity_id
    if orig_id:
        context_dict['orig_id']     = orig_id
    if action:  
        context_dict['action']      = action
    return context_dict

def entitydata_form_data(
        entity_id=None, orig_id=None, 
        type_id="testtype", orig_type=None,
        coll_id="testcoll", 
        action=None, cancel=None, update="Entity"):
    form_data_dict = (
        { 'Entity_label':       '%s data ... (%s/%s)'%(update, coll_id, type_id)
        , 'Entity_comment':     '%s description ... (%s/%s)'%(update, coll_id, type_id)
        , 'orig_id':            'orig_entity_id'
        , 'continuation_uri':   entitydata_list_type_uri(coll_id, orig_type or type_id)
        })
    if entity_id:
        form_data_dict['entity_id']         = entity_id
        form_data_dict['entity_type']       = type_id
        form_data_dict['Entity_label']      = '%s %s/%s/%s'%(update, coll_id, type_id, entity_id)
        form_data_dict['Entity_comment']    = '%s coll %s, type %s, entity %s'%(update, coll_id, type_id, entity_id)
        form_data_dict['orig_id']           = entity_id
        form_data_dict['orig_type']         = type_id
    if orig_id:
        form_data_dict['orig_id']           = orig_id
    if orig_type:
        form_data_dict['orig_type']         = orig_type
    if action:
        form_data_dict['action']            = action
    if cancel:
        form_data_dict['cancel']            = "Cancel"
    else:
        form_data_dict['save']              = 'Save'
    return form_data_dict

def entitydata_delete_confirm_form_data(entity_id=None):
    """
    Form data from entity deletion confirmation
    """
    return (
        { 'entity_id':     entity_id,
          'entity_delete': 'Delete'
        })

#   -----------------------------------------------------------------------------
#
#   ----- Entity list
#
#   -----------------------------------------------------------------------------

def entitylist_form_data(action, search="", list_id="Default_list", entities=None):
    """
    Form data from entity list form submission

    list_form_data = (
        { 'search_for':         ""
        , 'search':             "Find"
        , 'list_id':            "Default_list"
        , 'list_view':          "View"
        , 'entity_select':      ["{{entity.entity_id}}"]
        , 'new':                "New"
        , 'copy':               "Copy"
        , 'edit':               "Edit"
        , 'delete':             "Delete"
        , 'default_view':       "Set default"
        , 'customize':          "Customize"
        , 'continuation_uri':   "{{continuation_uri}}"
        })
    """
    form_actions = (
        { 'search':             "Find"
        , 'list_view':          "View"
        , 'new':                "New"
        , 'copy':               "Copy"
        , 'edit':               "Edit"
        , 'delete':             "Delete"
        , 'close':              "Close"
        , 'default_view':       "Set default"
        , 'customize':          "Customize"
        })
    form_data = (
        { 'search_for':         search
        , 'list_id':            list_id
        , 'continuation_uri':   collection_edit_uri("testcoll")
        })
    if entities is not None:
        form_data['entity_select'] = entities
    if action in form_actions:
        form_data[action] = form_actions[action]
    else:
        form_data[action] = action
    return form_data

# End.