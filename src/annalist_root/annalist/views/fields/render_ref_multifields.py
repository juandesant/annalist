"""
Renderer and value mapper for multiple fields displayed from a referenced entity.

The edit renderer provides for selection of the referenced entity, and stores its
id as the field value.

The view renderer displays a number of fields from the referenced entity corresponding
to a field group specified in the field definition.
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2015, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import sys
import traceback
import logging
log = logging.getLogger(__name__)

from django.http        import HttpResponse
from django.template    import Template, Context

from annalist.views.fields.render_select    import edit_select, Select_edit_renderer, SelectValueMapper
from annalist.views.fields.bound_field      import bound_field
from annalist.views.fields.render_fieldvalue    import (
    RenderFieldValue,
    get_field_edit_value,
    get_field_view_value
    )

col_head_view_template = (
        """<!-- views.fields.render_ref_mnultifield.col_head_view_template  (mode:{{render_mode}}) -->\n"""+
        """{% for f in group_bound_fields %}"""+
        """  <!-- field {{f}} -->"""+ #@@
        """  {% include f.field_render_mode with field=f %}"""+
        """{% endfor %}"""
        )

view_multifield = (
    { 'head':
        """
        <!-- view_multifield head (mode:{{render_mode}}) -->
        """
    , 'body':
        """
        <!-- view_multifield body (mode:{{render_mode}}) -->
        {% for f in group_bound_fields %}
          {% include f.field_render_mode with field=f %}\
        {% endfor %}
        """
    , 'tail':
        """
        <!-- view_multifield tail (mode:{{render_mode}})-->
        """
    })

class RenderMultiFields(object):
  """
  Render class for a field group in a referenced entity.
  """

  def __init__(self, templates=None):
    # Later, may introduce a template_file= option to read from templates directory
    """
    Creates a renderer object
    """
    # log.info("RenderMultiFields: __init__ %r"%(templates))
    super(RenderMultiFields, self).__init__()
    assert templates is not None, "RenderMultiFields template must be supplied (.edit or .view)"
    self._template_head  = Template(templates.get('head', ""))
    self._template_body  = Template(templates.get('body', "@@missing body@@"))
    self._template_tail  = Template(templates.get('tail', ""))
    return

  def __str__(self):
    return "RenderMultiFields %r"%(self._template_head)
    # return "RenderMultiFields %r, %s"%(self._template_head,self.render(context))

#   ----------------------------------------------------------------------------
#
#   Multi-field reference field renderer for viewing
#
#   ----------------------------------------------------------------------------

  def render(self, context):
    """
    Renders a repeating field group.

    `context`   is a dictionary-like object that provides information for the
                rendering operation.

    returns a string that is incorporated into the resulting web page.

    `context['field']` is a `bound_field` value that combines the field 
    definition, entity values and additional context information.  

    The entity value is either the entire entity that is currently 
    being rendered, or sub-element containing a list of repeated values that 
    are each formatted using the supplied body template.
    """
    log.info("RenderMultiFields.render (mode: %s)"%context['render_mode'])
    try:
        # log.info("RenderMultiFields.render field: %r"%(context['field'],))
        # log.info("RenderMultiFields.render descs: %r"%(context['field']['group_field_descs'],))
        target_vals = context['field']['target_value']
        extras      = context['field']['context_extra_values']
        log.debug("RenderMultiFields.render target_vals: %r"%(target_vals))
        group_fields = [ 
            bound_field(f, target_vals, context_extra_values=extras) 
            for f in context['field']['group_field_descs'] 
            ]
        group_dict = (
            { 'group_bound_fields':  group_fields
            , 'group_entity':        target_vals
            })
        log.info("RenderMultiFields.render group_dict: %r"%(group_dict))
        response_parts = [self._template_head.render(context)]
        with context.push(group_dict):
            response_parts.append(self._template_body.render(context))
        response_parts.append(self._template_tail.render(context))
    except Exception as e:
        log.exception("Exception in RenderMultiFields.render")
        ex_type, ex, tb = sys.exc_info()
        traceback.print_tb(tb)
        response_parts = (
            ["Exception in RenderMultiFields.render"]+
            [repr(e)]+
            traceback.format_exception(ex_type, ex, tb)+
            ["***RenderMultiFields.render***"]
            )
        del tb
    return "".join(response_parts)

#   ----------------------------------------------------------------------------
#
#   Multi-field reference value mapping
#
#   ----------------------------------------------------------------------------

class RefMultifieldValueMapper(SelectValueMapper):
    """
    Value mapper class for multifield reference

    Inherits all logic from SelectvalueMapper.
    """
    pass

#   ----------------------------------------------------------------------------
#
#   Return render objects for multiple field reference fields
#
#   ----------------------------------------------------------------------------

def get_ref_multifield_renderer():
    """
    Return field renderer object for value selector (with '+' button)
    """
    r = RenderFieldValue(
        col_head_view_template=col_head_view_template,
        view_renderer=RenderMultiFields(view_multifield),
        edit_renderer=Select_edit_renderer(edit_select)
        )
    return r

# End.
