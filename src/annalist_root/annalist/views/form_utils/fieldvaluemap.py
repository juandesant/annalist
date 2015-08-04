"""
Annalist class for processing a FieldValueMap in an annalist view value mapping table.

A FieldValueMap accepts a context field identifier and a field description structure,
and generates context values to drive rendering of that field in a form.
The template used is expected to iterate over the fields and render each one, e.g.:

    {% for field in fields %}
    {% include field.field_render_label_edit %}
    {% endfor %}

The iterated values of `field` provide additional values for the field rendering template,
including the value of the entity field to be presented.  Field descriptions are bound 
to entity values as the context elements are generated by this class. 

Entity and form field names used for this value are obtained from the field definition;
i.e. they are defined indirectly to support data-driven form generation.
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2014, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import logging
log = logging.getLogger(__name__)

from django.conf                        import settings

from annalist.views.fields.bound_field  import bound_field

class FieldValueMap(object):
    """
    Define an entry in an entity value mapping table corresponding to a
    field value and description, which is added to a list of such fields
    in the indicated context variable.

    c       request context field name for the field value mapping entry
    f       field description structure (cf. `FieldDescription`)

    NOTE: The form rendering template iterates over the context field values to be 
    added to the form display.  The constructor for this object appends the current
    field to a list of field value mappings at the indcated context field.
    """

    def __init__(self, c=None, f=None):
        self.c = c
        self.f = f
        self.e = f.get_field_property_uri()     # entity data key
        self.i = f.get_field_name()             # field data key
        return

    def __repr__(self):
        return (
            "FieldValueMap.c: %r\n"%(self.c)+
            "FieldValueMap.f: %r\n"%(self.f)+
            "FieldValueMap.e: %s\n"%(self.e)+
            "FieldValueMap.i: %s\n"%(self.i)
            )

    def map_entity_to_context(self, entityvals, context_extra_values=None):
        """
        Returns a bound_field, which is a dictionary-like of values to be added 
        to the display context under construction
        """
        # log.info("map entity %s to context %s, vals %r"%(self.e, self.i, entityvals))
        # log.info("map_entity_to_context: bound_field: context_extra_values %r"%(context_extra_values,))
        boundfield = bound_field(
            field_description=self.f, 
            entityvals=entityvals,
            context_extra_values=context_extra_values
            )
        return { self.c: boundfield }

    def map_form_to_entity(self, formvals, entityvals):
        """
        Returns singleton or empty dictionary to be included in the resulting entity.

        self.i is the form value key for the value to save.

        self.e is the entity property URI that receives the field value, or None if no 
        value is saved for this field.
        """
        if self.e:
            log.debug("FieldValueMap.map_form_to_entity %s, %r"%(self.e, formvals))
            v = formvals.get(self.i, None)
            self.f['field_value_mapper'].decode_store(v, entityvals, self.e)
        return entityvals

    def map_form_to_entity_repeated_item(self, formvals, entityvals, prefix):
        """
        Extra helper method used when mapping repeated field items to repeated entity values.
        The field name extracted is constructed using the supplied prefix string.

        Returns None if the prefixed value does not exist, which may be used as a loop
        termination condition.
        """
        if self.e:
            log.debug("FieldValueMap.map_form_to_entity_repeated_item %s, %r"%(self.e, formvals))
            v = formvals.get(prefix+self.i, None)
            if v is not None:
                self.f['field_value_mapper'].decode_store(v, entityvals, self.e)
                return v
        return None

    def get_structure_description(self):
        return (
            { 'field_type':     'FieldValueMap'
            , 'field_descr':    self.f
            , 'entity_field':   self.e
            , 'form_field':     self.i
            })

    def get_field_description(self):
        return self.f

# End.