"""
Generic entity edit view
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2014, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import copy

import logging
log = logging.getLogger(__name__)

from django.conf                    import settings
from django.http                    import HttpResponse
from django.http                    import HttpResponseRedirect
from django.core.urlresolvers       import resolve, reverse

from annalist                       import message

from annalist.models.recordview     import RecordView
from annalist.models.recordfield    import RecordField
from annalist.models.recordtypedata import RecordTypeData
from annalist.models.entitydata     import EntityData

from annalist.views.entityeditbase  import EntityEditBaseView, EntityDeleteConfirmedBaseView

#   -------------------------------------------------------------------------------------------
#
#   Entity edit view - form rendering and POST response handling
#
#   -------------------------------------------------------------------------------------------

class GenericEntityEditView(EntityEditBaseView):
    """
    View class for generic entity edit view

    The view to be displayted can be specified through the constructor
    (for predefined views) or through the HTTP request URTI parameters
    (for any view).
    """

    _entityformtemplate = 'annalist_entity_edit.html'

    def __init__(self):
        super(GenericEntityEditView, self).__init__()
        return

    def get_view_id(self, view_id):
        if not view_id:
            log.warning("GenericEntityEditView: No view identifier provided")
        return view_id

    # GET

    def get(self, request, 
            coll_id=None, type_id=None, entity_id=None, 
            view_id=None, action=None):
        """
        Create a form for editing an entity.
        """
        log.log(settings.TRACE_FIELD_VALUE,
            "views.entityedit.get %s"%(self.get_request_path())
            )
        log.log(settings.TRACE_FIELD_VALUE,
            "    coll_id %s, type_id %s, entity_id %s, view_id %s, action %s"%
              (coll_id, type_id, entity_id, view_id, action)
            )
        http_response = (
            self.get_coll_data(coll_id, host=self.get_request_host()) or
            self.form_edit_auth(action, self.collection._entityuri) or
            self.get_type_data(type_id) or
            self.get_view_data(self.get_view_id(view_id))
            )
        if http_response:
            return http_response
        # Set up RecordType-specific values
        entity_id  = self.get_entityid(action, self.entityparent, entity_id)
        # Create local entity object or load values from existing
        entity_initial_values = (
            { "rdfs:label":   "Entity '%s' of type '%s' in collection '%s'"%
                              (entity_id, type_id, coll_id)
            , "rdfs:comment": ""
            })
        entity = self.get_entity(action, self.entityparent, entity_id, entity_initial_values)
        if entity is None:
            return self.error(
                dict(self.error404values(),
                    message=message.DOES_NOT_EXIST%{'id': entity_initial_values['rdfs:label']}
                    )
                )
        type_ids = [ t.get_id() for t in self.collection.types() ]
        # Set up initial view context
        # @@TODO: move view access logic from get_form_entityvaluemap (see there for details)
        self._entityvaluemap = self.get_form_entityvaluemap(self.get_view_id(view_id))
        viewcontext = self.map_value_to_context(entity,
            title               = self.site_data()["title"],
            continuation_uri    = request.GET.get('continuation_uri', ""),
            heading             = entity_initial_values['rdfs:label'],
            action              = action,
            coll_id             = coll_id,
            type_id             = type_id,
            type_ids            = type_ids,
            orig_id             = entity_id,
            orig_type           = type_id,
            view_id             = view_id
            )
        # generate and return form data
        return (
            self.render_html(viewcontext, self._entityformtemplate) or 
            self.error(self.error406values())
            )

    # POST

    def post(self, request,
            coll_id=None, type_id=None, entity_id=None, 
            view_id=None, action=None):
        """
        Handle response from generic entity editing form.
        """
        log.debug("views.entityedit.post %s"%(self.get_request_path()))
        log.debug(
            "    coll_id %s, type_id %s, entity_id %s, view_id %s, action %s"%
              (coll_id, type_id, entity_id, view_id, action)
            )
        log.debug("  form data %r"%(request.POST))
        http_response = (
            self.get_coll_data(coll_id, host=self.get_request_host()) or
            self.form_edit_auth(action, self.collection._entityuri) or
            self.get_type_data(type_id) or
            self.get_view_data(self.get_view_id(view_id))
            )
        if http_response:
            return http_response
        # Get key POST values
        # Except for entity_id, use values from URI when form does not have corresponding fields
        entity_id            = request.POST.get('entity_id', None)
        orig_entity_id       = request.POST.get('orig_id', entity_id)
        entity_type          = request.POST.get('entity_type', type_id)
        orig_entity_type     = request.POST.get('orig_type', type_id)
        continuation_uri     = (request.POST.get('continuation_uri', None) or
            self.view_uri('AnnalistEntityDefaultListType', coll_id=coll_id, type_id=type_id)
            )
        view_id              = request.POST.get('view_id', view_id)
        action               = request.POST.get('action', action)
        # log.info(
        #     "    coll_id %s, type_id %s, entity_id %s, view_id %s, action %s"%
        #       (coll_id, type_id, entity_id, view_id, action)
        #     )
        # log.info("continuation_uri %s, type_id %s"%(continuation_uri, type_id))
        #
        # Retrieve original entity content for any values not included in form 
        entity_initial_values = {}
        context_extra_values = self.get_entity(
            action, self.entityparent, orig_entity_id, entity_initial_values
            )
        if context_extra_values is None:
            context_extra_values = entity_initial_values
        type_ids = [ t.get_id() for t in self.collection.types() ]
        context_extra_values = (
            { 'title':            self.site_data()["title"]
            , 'heading':          "Entity '%s' of type '%s' in collection '%s'"%
                                  (entity_id, type_id, coll_id)
            , 'action':           action
            , 'continuation_uri': continuation_uri
            , 'coll_id':          coll_id
            , 'type_id':          type_id
            , 'type_ids':         type_ids
            , 'orig_id':          orig_entity_id
            , 'orig_type':        orig_entity_type
            , 'view_id':          view_id
            })
        message_vals = {'id': entity_id, 'type_id': type_id, 'coll_id': coll_id}
        messages = (
            { 'parent_heading':         self.entitymessages['parent_heading']%message_vals
            , 'parent_missing':         self.entitymessages['parent_missing']%message_vals
            , 'entity_heading':         self.entitymessages['entity_heading']%message_vals
            , 'entity_invalid_id':      self.entitymessages['entity_invalid_id']%message_vals
            , 'entity_exists':          self.entitymessages['entity_exists']%message_vals
            , 'entity_not_exists':      self.entitymessages['entity_not_exists']%message_vals
            , 'entity_type_heading':    self.entitymessages['entity_type_heading']%message_vals
            , 'entity_type_invalid':    self.entitymessages['entity_type_invalid']%message_vals
            })
        # Process form response and respond accordingly
        self._entityvaluemap = self.get_form_entityvaluemap(self.get_view_id(view_id))
        if not self.entityparent._exists():
            # Create RecordTypeData when not already exists
            RecordTypeData.create(self.collection, self.entityparent.get_id(), {})
        # log.info(
        #     "self.form_response: entity_id %s, orig_entity_id %s, type_id %s, action %s"%
        #       (entity_id, orig_entity_id, type_id, action)
        #     )
        return self.form_response(
            request, action, self.entityparent, 
            entity_id, orig_entity_id, 
            entity_type, orig_entity_type,
            self.entitymessages, context_extra_values
            )

# End.
