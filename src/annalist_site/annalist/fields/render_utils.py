"""
This module contains utilities for use in conjunction with field renderers.
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2014, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import logging
log = logging.getLogger(__name__)

import re

# from annalist.fields.render_text    import RenderText
from render_text    import RenderText

class bound_field(object):
    """
    Class representing an entity bound to a field description, 
    which can be used as input for data driven rendering of a form field.

    The field description contains information used to extract the field
    value from the entity.

    This class, and in particular its `__getattr__` method, is provided to 
    allow indirected access to an entity value fields to be performed using a 
    Django template using, e.g., "{{ field.field_value }}" (thus satisfying the 
    Django design goal that computation is handled in the python code rather 
    than the template, though in this case the computation us handled while
    rather than before the page is rendered).

    See also: http://docs.python.org/2/reference/datamodel.html#slots

    >>> entity = {"foo": "foo_val", "bar": "bar_val" }
    >>> field_foo_desc = {"field_property_uri": "foo", "field_type": "foo_type"}
    >>> field_foo = bound_field(field_foo_desc, entity)
    >>> field_foo.field_type
    'foo_type'
    >>> field_foo.field_value
    'foo_val'
    >>> field_bar_desc = {"field_property_uri": "bar", "field_type": "bar_type"}
    >>> field_bar = bound_field(field_bar_desc, entity)
    >>> field_bar.field_type
    'bar_type'
    >>> field_bar.field_value
    'bar_val'
    """

    __slots__ = ("_field_description", "_entity")

    def __init__(self, field_description=None, entity=None):
        """
        Initialize a bound_field object.

        field_description   is a dictionary-like object describing a display
                            field.  See assignment of `field_context` in 
                            `views.entityeditbase` for more details of this.
        entity              is an entity from which a value to be rendered is
                            obtained.  The specific field value used is defined
                            by the combination with `field_description`
        """
        self._field_description = field_description
        self._entity            = entity
        return

    def __getattr__(self, name):
        """
        Get a bound field description attribute.  If the attribute name is "field_value"
        then the value corresponding to the field description is retrieved from the entity,
        otherwise the named attribute is retrieved from thge field description.
        """
        if name == "field_value":
            return self._entity[self._field_description['field_property_uri']]
        else:
            return self._field_description[name]

def get_edit_renderer(renderid):
    """
    Returns an field edit renderer object that can be referenced in a 
    Django template "{% include ... %}" element.

    This version returns the name of a template to render the form.
    With future versions of Django (>=1.7), and alternative is to return an
    object with a `.render(context)` method that returns a string to be
    included in the resulting page:
        The variable may also be any object with a render() method that accepts 
        a context. This allows you to reference a compiled Template in your context.
        - https://docs.djangoproject.com/en/dev/ref/templates/builtins/#include
    """
    # @@TODO: currently just a minimal placeholder
    if renderid == "annal:field_render/Text":
        return "field/annalist_edit_text.html"
        # return RenderText()
    if renderid == "annal:field_render/Slug":
        return "field/annalist_edit_text.html"
    if renderid == "annal:field_render/Textarea":
        return "field/annalist_edit_textarea.html"
    log.warning("get_edit_renderer: %s not found"%renderid)
    return None

def get_view_renderer(renderid):
    """
    Returns a field view renderer object that can be referenced in a 
    Django template "{% include ... %}" element.

    This version returns the name of a template to render the form.
    With future versions of Django (>=1.7), and alternative is to return an
    object with a `.render(context)` method that returns a string to be
    included in the resulting page:
        The variable may also be any object with a render() method that accepts 
        a context. This allows you to reference a compiled Template in your context.
        - https://docs.djangoproject.com/en/dev/ref/templates/builtins/#include
    """
    # @@TODO: currently just a minimal placeholder
    if renderid == "annal:field_render/Text":
        return "field/annalist_view_text.html"
        # return RenderText()
    if renderid == "annal:field_render/Slug":
        return "field/annalist_view_text.html"
    if renderid == "annal:field_render/Textarea":
        return "field/annalist_view_textarea.html"
    log.warning("get_edit_renderer: %s not found"%renderid)
    return None

def get_head_renderer(renderid):
    """
    Returns a field list heading renderer object that can be referenced in a 
    Django template "{% include ... %}" element.
    """
    if renderid == "annal:field_render/Text":
        return "field/annalist_head_text.html"
    if renderid == "annal:field_render/Slug":
        return "field/annalist_head_text.html"
    log.warning("get_head_renderer: %s not found"%renderid)
    return None

def get_item_renderer(renderid):
    """
    Returns a field list row-item renderer object that can be referenced in a 
    Django template "{% include ... %}" element.
    """
    if renderid == "annal:field_render/Text":
        return "field/annalist_item_text.html"
    if renderid == "annal:field_render/Slug":
        return "field/annalist_item_text.html"
    log.warning("get_item_renderer: %s not found"%renderid)
    return None

def get_placement_class(placement):
    """
    Returns placement classes corresponding to placement string provided.

    >>> get_placement_class("small:0,12")
    'small-12 columns'
    >>> get_placement_class("medium:0,12")
    'medium-12 columns'
    >>> get_placement_class("large:0,12")
    'large-12 columns'
    >>> get_placement_class("small:0,12;medium:0,4")
    'small-12 medium-4 columns'
    >>> get_placement_class("small:0,12;medium:0,6;large:0,4")
    'small-12 medium-6 large-4 columns'
    """
    ppr = re.compile(r"^(small|medium|large):(\d+),(\d+)$")
    ps = placement.split(';')
    c = ""
    for p in ps:
        pm = ppr.match(p)
        if not pm:
            break
        c += pm.group(1)+"-"+pm.group(3)+" "
    c += "columns"
    return c

if __name__ == "__main__":
    import doctest
    doctest.testmod()

# End.
