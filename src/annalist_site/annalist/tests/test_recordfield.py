"""
Tests for RecordField metadata editing view
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2014, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import os
import json
import unittest

import logging
log = logging.getLogger(__name__)

from django.conf                    import settings
from django.db                      import models
from django.http                    import QueryDict
from django.contrib.auth.models     import User
from django.test                    import TestCase # cf. https://docs.djangoproject.com/en/dev/topics/testing/tools/#assertions
from django.test.client             import Client

from annalist.identifiers           import RDF, RDFS, ANNAL
from annalist                       import layout
from annalist.models.site           import Site
from annalist.models.collection     import Collection
from annalist.models.recordfield    import RecordField
# from annalist.models.recordtype     import RecordType
# from annalist.models.recordtypedata import RecordTypeData
# from annalist.models.entitydata     import EntityData

from annalist.views.entityedit      import GenericEntityEditView

from tests                          import TestHost, TestHostUri, TestBasePath, TestBaseUri, TestBaseDir
from tests                          import init_annalist_test_site
from AnnalistTestCase               import AnnalistTestCase
from entity_testfielddata           import (
    recordfield_dir,
    recordfield_uri, recordfield_view_uri,
    recordfield_init_keys, recordfield_value_keys, recordfield_load_keys,
    recordfield_create_values, recordfield_values, recordfield_read_values,
    entitydata_recordfield_view_context_data,
    entitydata_recordfield_view_form_data
    )

from entity_testutils               import (
    # recordtype_create_values, 
    collection_create_values,
    # site_dir, 
    # collection_dir, 
    # recordtype_dir, recorddata_dir,  entitydata_dir,
    # collection_edit_uri,
    # recordtype_edit_uri,
    # recordtype_form_data,
    # entitydata_value_keys, entitydata_create_values, entitydata_values,
    # entitydata_recordtype_view_context_data, 
    # # entitydata_context_data, 
    # entitydata_recordtype_view_form_data,
    # # entitydata_form_data, 
    # entitydata_delete_confirm_form_data,
    site_title
    )
from entity_testentitydata          import (
    entity_uri, entitydata_edit_uri, entitydata_list_type_uri
    )

#   -----------------------------------------------------------------------------
#
#   RecordField (model) tests
#
#   -----------------------------------------------------------------------------

class RecordFieldTest(AnnalistTestCase):
    """
    Tests for RecordField object interface
    """

    def setUp(self):
        init_annalist_test_site()
        self.testsite = Site(TestBaseUri, TestBaseDir)
        # self.sitedata = SiteData(self.testsite)
        self.testcoll = Collection(self.testsite, "testcoll")
        return

    def tearDown(self):
        return

    def test_RecordFieldTest(self):
        self.assertEqual(RecordField.__name__, "RecordField", "Check RecordField class name")
        return

    def test_recordfield_init(self):
        t = RecordField(self.testcoll, "testfield")
        self.assertEqual(t._entitytype,     ANNAL.CURIE.RecordField)
        self.assertEqual(t._entityfile,     layout.FIELD_META_FILE)
        self.assertEqual(t._entityref,      layout.META_FIELD_REF)
        self.assertEqual(t._entityid,       "testfield")
        self.assertEqual(t._entityuri,      TestHostUri + recordfield_uri("testcoll", "testfield"))
        self.assertEqual(t._entitydir,      recordfield_dir(field_id="testfield"))
        self.assertEqual(t._values,         None)
        return

    def test_recordfield1_data(self):
        t = RecordField(self.testcoll, "field1")
        self.assertEqual(t.get_id(), "field1")
        self.assertEqual(t.get_type_id(), "_field")
        self.assertIn("/c/testcoll/_annalist_collection/fields/field1/", t.get_uri())
        t.set_values(recordfield_create_values(field_id="field1"))
        td = t.get_values()
        self.assertEqual(set(td.keys()), set(recordfield_init_keys()))
        v = recordfield_values(field_id="field1")
        self.assertDictionaryMatch(td, v)
        return

    def test_recordfield2_data(self):
        t = RecordField(self.testcoll, "field2")
        self.assertEqual(t.get_id(), "field2")
        self.assertEqual(t.get_type_id(), "_field")
        self.assertIn("/c/testcoll/_annalist_collection/fields/field2/", t.get_uri())
        t.set_values(recordfield_create_values(field_id="field2"))
        td = t.get_values()
        self.assertEqual(set(td.keys()), set(recordfield_init_keys()))
        v = recordfield_values(field_id="field2")
        self.assertDictionaryMatch(td, v)
        return

    def test_recordfield_create_load(self):
        t  = RecordField.create(self.testcoll, "field1", recordfield_create_values(field_id="field1"))
        td = RecordField.load(self.testcoll, "field1").get_values()
        v  = recordfield_read_values(field_id="field1")
        self.assertKeysMatch(td, v)
        self.assertDictionaryMatch(td, v)
        return

    def test_recordfield_default_data(self):
        t = RecordField.load(self.testcoll, "Field_type", altparent=self.testsite)
        self.assertEqual(t.get_id(), "Field_type")
        self.assertIn("/c/testcoll/_annalist_collection/fields/Field_type", t.get_uri())
        self.assertEqual(t.get_type_id(), "_field")
        td = t.get_values()
        self.assertEqual(set(td.keys()), set(recordfield_load_keys()))
        v = recordfield_read_values(field_id="Field_type")
        v.update(
            { '@id':                "annal:fields/Field_type"
            , 'rdfs:label':         "Field value type"
            , 'rdfs:comment':       "Type of display field.  "+
                                    "This encompasses the actual form of the rendered value and "+
                                    "the type of underlying record data that is formatted, and "+
                                    "any defaults of other values that may be applied to the field."
            , 'annal:type':         "annal:Field"
            , 'annal:uri':          "http://test.example.com/testsite/c/testcoll/d/_field/Field_type/"
            , 'annal:value_type':   "annal:RenderType"
            , 'annal:field_render': "annal:field_render/Identifier"
            , 'annal:placeholder':  "(field value type)"
            , 'annal:property_uri': "annal:field_render"
            })
        self.assertDictionaryMatch(td, v)
        return

#   -----------------------------------------------------------------------------
#
#   RecordField edit view tests
#
#   -----------------------------------------------------------------------------

class FieldEditViewTest(AnnalistTestCase):
    """
    Tests for record type edit views
    """

    def setUp(self):
        init_annalist_test_site()
        self.testsite = Site(TestBaseUri, TestBaseDir)
        self.testcoll = Collection.create(self.testsite, "testcoll", collection_create_values("testcoll"))
        self.user     = User.objects.create_user('testuser', 'user@test.example.com', 'testpassword')
        self.user.save()
        self.client   = Client(HTTP_HOST=TestHost)
        loggedin      = self.client.login(username="testuser", password="testpassword")
        self.assertTrue(loggedin)
        self.no_options = ['(no options)']
        return

    def tearDown(self):
        return

    #   -----------------------------------------------------------------------------
    #   Helpers
    #   -----------------------------------------------------------------------------

    def _create_view_data(self, field_id, update="Field"):
        "Helper function creates view data with supplied field_id"
        e = RecordField.create(self.testcoll, field_id, 
            recordfield_create_values(field_id=field_id, update=update)
            )
        return e    

    def _check_view_data_values(self, field_id, update="Field", parent=None):
        "Helper function checks content of form-updated record type entry with supplied field_id"
        self.assertTrue(RecordField.exists(self.testcoll, field_id, altparent=self.testsite))
        e = RecordField.load(self.testcoll, field_id, altparent=self.testsite)
        self.assertEqual(e.get_id(), field_id)
        self.assertEqual(e.get_uri(), TestHostUri + recordfield_uri("testcoll", field_id))
        v = recordfield_values(field_id=field_id, update=update)
        self.assertDictionaryMatch(e.get_values(), v)
        return e

    def _check_context_fields(self, response, 
            field_id="(?field_id)", 
            field_type="(?field_type)",
            field_label="(?field_label)",
            field_comment="(?field_comment)",
            field_placeholder="(?field_placeholder)",
            field_property="(?field_property)",
            field_placement="(?field_placement)"
            ):
        r = response
        self.assertEqual(len(r.context['fields']), 7)        
        # 1st field - Id
        field_id_help = (
            "A short identifier that distinguishes this field from all other fields in the same collection.  "+
            "A given field may occur in a number of different record types and/or views, "+
            "so is scoped to the containing collection."
            )
        self.assertEqual(r.context['fields'][0]['field_id'], 'Field_id')
        self.assertEqual(r.context['fields'][0]['field_name'], 'entity_id')
        self.assertEqual(r.context['fields'][0]['field_label'], 'Id')
        self.assertEqual(r.context['fields'][0]['field_help'], field_id_help)
        self.assertEqual(r.context['fields'][0]['field_placeholder'], "(field id)")
        self.assertEqual(r.context['fields'][0]['field_property_uri'], "annal:id")
        self.assertEqual(r.context['fields'][0]['field_render_view'], "field/annalist_view_entityref.html")
        self.assertEqual(r.context['fields'][0]['field_render_edit'], "field/annalist_edit_text.html")
        self.assertEqual(r.context['fields'][0]['field_placement'].field, "small-12 medium-6 columns")
        self.assertEqual(r.context['fields'][0]['field_value_type'], "annal:Slug")
        self.assertEqual(r.context['fields'][0]['field_value'], field_id)
        self.assertEqual(r.context['fields'][0]['options'], self.no_options)
        # 2nd field - Label
        field_type_help = (
            "Type of display field.  "+
            "This encompasses the actual form of the rendered value and "+
            "the type of underlying record data that is formatted, and "+
            "any defaults of other values that may be applied to the field."
            )
        self.assertEqual(r.context['fields'][1]['field_id'], 'Field_type')
        self.assertEqual(r.context['fields'][1]['field_name'], 'Field_type')
        self.assertEqual(r.context['fields'][1]['field_label'], 'Field value type')
        self.assertEqual(r.context['fields'][1]['field_help'], field_type_help)
        self.assertEqual(r.context['fields'][1]['field_placeholder'], "(field value type)")
        self.assertEqual(r.context['fields'][1]['field_property_uri'], "annal:field_render")
        self.assertEqual(r.context['fields'][1]['field_render_view'], "field/annalist_view_entityref.html")
        self.assertEqual(r.context['fields'][1]['field_render_edit'], "field/annalist_edit_text.html")
        self.assertEqual(r.context['fields'][1]['field_placement'].field, "small-12 medium-6 right columns")
        self.assertEqual(r.context['fields'][1]['field_value_type'], "annal:RenderType")
        self.assertEqual(r.context['fields'][1]['field_value'], field_type)
        self.assertEqual(r.context['fields'][1]['options'], self.no_options)
        # 3rd field - Label
        field_label_help = (
            "Short string used to label value in form display, or as heading of list column"
            )
        self.assertEqual(r.context['fields'][2]['field_id'], 'Field_label')
        self.assertEqual(r.context['fields'][2]['field_name'], 'Field_label')
        self.assertEqual(r.context['fields'][2]['field_label'], 'Label')
        self.assertEqual(r.context['fields'][2]['field_help'], field_label_help)
        self.assertEqual(r.context['fields'][2]['field_placeholder'], "(field label)")
        self.assertEqual(r.context['fields'][2]['field_property_uri'], "rdfs:label")
        self.assertEqual(r.context['fields'][2]['field_render_view'], "field/annalist_view_text.html")
        self.assertEqual(r.context['fields'][2]['field_render_edit'], "field/annalist_edit_text.html")
        self.assertEqual(r.context['fields'][2]['field_placement'].field, "small-12 columns")
        self.assertEqual(r.context['fields'][2]['field_value_type'], "annal:Text")
        self.assertEqual(r.context['fields'][2]['field_value'], field_label)
        self.assertEqual(r.context['fields'][2]['options'], self.no_options)
        # 4th field - comment
        field_comment_help = (
            "Descriptive text explaining how field is intended to be used.  "+
            "This text may be used to provide content for a tooltip "+
            "associated with the field display in a form."
            )
        field_comment_placeholder = (
            "(field usage commentary or help text)"
            )
        self.assertEqual(r.context['fields'][3]['field_id'], 'Field_comment')
        self.assertEqual(r.context['fields'][3]['field_name'], 'Field_comment')
        self.assertEqual(r.context['fields'][3]['field_label'], 'Help')
        self.assertEqual(r.context['fields'][3]['field_help'], field_comment_help)
        self.assertEqual(r.context['fields'][3]['field_placeholder'], field_comment_placeholder)
        self.assertEqual(r.context['fields'][3]['field_property_uri'], "rdfs:comment")
        self.assertEqual(r.context['fields'][3]['field_render_view'],   "field/annalist_view_textarea.html")
        self.assertEqual(r.context['fields'][3]['field_render_edit'],   "field/annalist_edit_textarea.html")
        self.assertEqual(r.context['fields'][3]['field_placement'].field, "small-12 columns")
        self.assertEqual(r.context['fields'][3]['field_value_type'], "annal:Longtext")
        self.assertEqual(r.context['fields'][3]['field_value'], field_comment)
        self.assertEqual(r.context['fields'][3]['options'], self.no_options)
        # 5th field - URI
        field_placeholder_help = (
            "Placeholder string displayed in field until actual value is selected"
            )
        self.assertEqual(r.context['fields'][4]['field_id'], 'Field_placeholder')
        self.assertEqual(r.context['fields'][4]['field_name'], 'Field_placeholder')
        self.assertEqual(r.context['fields'][4]['field_label'], 'Placeholder')
        self.assertEqual(r.context['fields'][4]['field_help'], field_placeholder_help)
        self.assertEqual(r.context['fields'][4]['field_placeholder'], "(placeholder text)")
        self.assertEqual(r.context['fields'][4]['field_property_uri'], "annal:placeholder")
        self.assertEqual(r.context['fields'][4]['field_render_view'], "field/annalist_view_text.html")
        self.assertEqual(r.context['fields'][4]['field_render_edit'], "field/annalist_edit_text.html")
        self.assertEqual(r.context['fields'][4]['field_placement'].field, "small-12 columns")
        self.assertEqual(r.context['fields'][4]['field_value_type'], "annal:Text")
        self.assertEqual(r.context['fields'][4]['field_value'], field_placeholder)
        self.assertEqual(r.context['fields'][4]['options'], self.no_options)
        # 6th field - Field_property
        field_property_help = (
            "Property URI (or CURIE) used to represent this field data in a record"
            )
        self.assertEqual(r.context['fields'][5]['field_id'], 'Field_property')
        self.assertEqual(r.context['fields'][5]['field_name'], 'Field_property')
        self.assertEqual(r.context['fields'][5]['field_label'], 'Property')
        self.assertEqual(r.context['fields'][5]['field_help'], field_property_help)
        self.assertEqual(r.context['fields'][5]['field_placeholder'], "(property URI or CURIE)")
        self.assertEqual(r.context['fields'][5]['field_property_uri'], "annal:property_uri")
        self.assertEqual(r.context['fields'][5]['field_render_view'], "field/annalist_view_entityref.html")
        self.assertEqual(r.context['fields'][5]['field_render_edit'], "field/annalist_edit_text.html")
        self.assertEqual(r.context['fields'][5]['field_placement'].field, "small-12 columns")
        self.assertEqual(r.context['fields'][5]['field_value_type'], "annal:Identifier")
        self.assertEqual(r.context['fields'][5]['field_value'], field_property)
        self.assertEqual(r.context['fields'][5]['options'], self.no_options)
        # 7th field - ??
        field_placement_help = (
            "Size of displayed field, and hints for its position in a record display"
            )
        field_placement_placeholder = (
            "(field display size and placement details)"
            )
        self.assertEqual(r.context['fields'][6]['field_id'], 'Field_placement')
        self.assertEqual(r.context['fields'][6]['field_name'], 'Field_placement')
        self.assertEqual(r.context['fields'][6]['field_label'], 'Size and position')
        self.assertEqual(r.context['fields'][6]['field_help'], field_placement_help)
        self.assertEqual(r.context['fields'][6]['field_placeholder'], field_placement_placeholder)
        self.assertEqual(r.context['fields'][6]['field_property_uri'], "annal:field_placement")
        self.assertEqual(r.context['fields'][6]['field_render_view'], "field/annalist_view_text.html")
        self.assertEqual(r.context['fields'][6]['field_render_edit'], "field/annalist_edit_text.html")
        self.assertEqual(r.context['fields'][6]['field_placement'].field, "small-12 columns")
        self.assertEqual(r.context['fields'][6]['field_value_type'], "annal:Placement")
        self.assertEqual(r.context['fields'][6]['field_value'], field_placement)
        self.assertEqual(r.context['fields'][6]['options'], self.no_options)

    #   -----------------------------------------------------------------------------
    #   Form rendering tests
    #   -----------------------------------------------------------------------------

    def test_GenericEntityEditView(self):
        self.assertEqual(GenericEntityEditView.__name__, "GenericEntityEditView", "Check GenericEntityEditView class name")
        return

    def test_get_form_rendering(self):
        u = entitydata_edit_uri("new", "testcoll", "_field", view_id="Field_view")
        r = self.client.get(u+"?continuation_uri=/xyzzy/")
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        # log.info(r.content)
        self.assertContains(r, site_title("<title>%s</title>"))
        self.assertContains(r, "<h3>'_field' data in collection 'testcoll'</h3>")
        formrow1col1 = """
            <div class="small-12 medium-6 columns">
                <div class="row">
                    <div class="view_label small-12 medium-4 columns">
                        <p>Id</p>
                    </div>
                    <div class="small-12 medium-8 columns">
                        <input type="text" size="64" name="entity_id" value="00000001"/>
                    </div>
                </div>
            </div>
            """
        formrow1col2 = """
            <div class="small-12 medium-6 right columns">
                <div class="row">
                    <div class="view_label small-12 medium-4 columns">
                        <p>Field value type</p>
                    </div>
                    <div class="small-12 medium-8 columns">
                        <input type="text" size="64" name="Field_type" value="(field value type)"/>
                    </div>
                </div>
            </div>
            """
        formrow2 = """
            <div class="small-12 columns">
                <div class="row">
                    <div class="view_label small-12 medium-2 columns">
                        <p>Label</p>
                    </div>
                    <div class="small-12 medium-10 columns">
                        <input type="text" size="64" name="Field_label" value="Entity &#39;00000001&#39; of type &#39;_field&#39; in collection &#39;testcoll&#39;"/>
                    </div>
                </div>
            </div>
            """
        formrow3 = """
            <div class="small-12 columns">
                <div class="row">
                    <div class="view_label small-12 medium-2 columns">
                        <p>Help</p>
                    </div>
                    <div class="small-12 medium-10 columns">
                                <textarea cols="64" rows="6" name="Field_comment" class="small-rows-4 medium-rows-8"></textarea>
                    </div>
                </div>
            </div>
            """
        formrow4 = """
            <div class="small-12 columns">
                <div class="row">
                    <div class="view_label small-12 medium-2 columns">
                        <p>Placeholder</p>
                    </div>
                    <div class="small-12 medium-10 columns">
                        <input type="text" size="64" name="Field_placeholder" value="(placeholder text)"/>
                    </div>
                </div>
            </div>
            """
        formrow5 = """
            <div class="small-12 columns">
                <div class="row">
                    <div class="view_label small-12 medium-2 columns">
                        <p>Property</p>
                    </div>
                    <div class="small-12 medium-10 columns">
                        <input type="text" size="64" name="Field_property" value="(property URI or CURIE)"/>
                    </div>
                </div>
            </div>
            """
        formrow6 = """
            <div class="small-12 columns">
                <div class="row">
                    <div class="view_label small-12 medium-2 columns">
                        <p>Size and position</p>
                    </div>
                    <div class="small-12 medium-10 columns">
                        <input type="text" size="64" name="Field_placement" 
                               value="(field display size and placement details)"/>
                    </div>
                </div>
            </div>
            """
        self.assertContains(r, formrow1col1, html=True)
        self.assertContains(r, formrow1col2, html=True)
        self.assertContains(r, formrow2, html=True)
        self.assertContains(r, formrow3, html=True)
        self.assertContains(r, formrow4, html=True)
        self.assertContains(r, formrow5, html=True)
        self.assertContains(r, formrow6, html=True)
        return

    def test_get_new(self):
        u = entitydata_edit_uri("new", "testcoll", "_field", view_id="Field_view")
        r = self.client.get(u+"?continuation_uri=/xyzzy/")
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        # Test context
        field_uri = entity_uri(type_id="_field", entity_id="00000001")
        self.assertEqual(r.context['title'],            site_title())
        self.assertEqual(r.context['coll_id'],          "testcoll")
        self.assertEqual(r.context['type_id'],          "_field")
        self.assertEqual(r.context['entity_id'],        "00000001")
        self.assertEqual(r.context['orig_id'],          "00000001")
        self.assertEqual(r.context['entity_uri'],       TestHostUri + field_uri)
        self.assertEqual(r.context['action'],           "new")
        self.assertEqual(r.context['continuation_uri'], "/xyzzy/")
        # Fields
        self._check_context_fields(r, 
            field_id="00000001",
            field_type="(field value type)",
            field_label="Entity '00000001' of type '_field' in collection 'testcoll'",
            field_comment="",
            field_placeholder="(placeholder text)",
            field_property="(property URI or CURIE)",
            field_placement="(field display size and placement details)"
            )
        return

    def test_get_new_no_continuation(self):
        u = entitydata_edit_uri("new", "testcoll", "_field", view_id="Field_view")
        r = self.client.get(u)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        # Test context
        field_uri = entity_uri(type_id="_field", entity_id="00000001")
        self.assertEqual(r.context['title'],            site_title())
        self.assertEqual(r.context['coll_id'],          "testcoll")
        self.assertEqual(r.context['type_id'],          "_field")
        self.assertEqual(r.context['entity_id'],        "00000001")
        self.assertEqual(r.context['orig_id'],          "00000001")
        self.assertEqual(r.context['entity_uri'],       TestHostUri + field_uri)
        self.assertEqual(r.context['action'],           "new")
        self.assertEqual(r.context['continuation_uri'], "")
        return

    def test_get_edit(self):
        u = entitydata_edit_uri("edit", "testcoll", "_field", entity_id="Type_label", view_id="Field_view")
        # log.info("test_get_edit uri %s"%u)
        r = self.client.get(u+"?continuation_uri=/xyzzy/")
        # log.info("test_get_edit resp %s"%r.content)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        self.assertContains(r, site_title("<title>%s</title>"))
        self.assertContains(r, "<h3>'_field' data in collection 'testcoll'</h3>")
        # Test context
        self.assertEqual(r.context['title'],            site_title())
        self.assertEqual(r.context['coll_id'],          "testcoll")
        self.assertEqual(r.context['type_id'],          "_field")
        self.assertEqual(r.context['entity_id'],        "Type_label")
        self.assertEqual(r.context['orig_id'],          "Type_label")
        self.assertEqual(r.context['entity_uri'],       TestHostUri + entity_uri("testcoll", "_field", "Type_label"))
        self.assertEqual(r.context['action'],           "edit")
        self.assertEqual(r.context['continuation_uri'], "/xyzzy/")
        # Fields
        self._check_context_fields(r, 
            field_id="Type_label",
            field_type="annal:field_render/Text",    # @@TODO review usage here
            field_label="Label",
            field_comment="Short string used to describe record type when displayed",
            field_placeholder="(label)",
            field_property="rdfs:label",
            field_placement="(field display size and placement details)"
            )
        return

    def test_get_edit_not_exists(self):
        u = entitydata_edit_uri("edit", "testcoll", "_field", entity_id="fieldnone", view_id="Field_view")
        r = self.client.get(u+"?continuation_uri=/xyzzy/")
        self.assertEqual(r.status_code,   404)
        self.assertEqual(r.reason_phrase, "Not found")
        self.assertContains(r, "<title>Annalist error</title>", status_code=404)
        self.assertContains(r, "<h3>404: Not found</h3>", status_code=404)
        # log.info(r.content)
        self.assertContains(r, 
            "<p>Entity &#39;fieldnone&#39; of type &#39;_field&#39; "+
            "in collection &#39;testcoll&#39; does not exist</p>", 
            status_code=404
            )
        return

    #   -----------------------------------------------------------------------------
    #   Form response tests
    #   -----------------------------------------------------------------------------

    #   -------- new entity --------

    def test_post_new_field(self):
        self.assertFalse(RecordField.exists(self.testcoll, "newfield"))
        f = entitydata_recordfield_view_form_data(field_id="newfield", action="new")
        u = entitydata_edit_uri("new", "testcoll", "_field", view_id="Field_view")
        r = self.client.post(u, f)
        # print r.content
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        self.assertEqual(r['location'], TestHostUri + entitydata_list_type_uri("testcoll", "_field"))
        # Check new entity data created
        self._check_view_data_values("newfield")
        return

    def test_post_new_field_no_continuation(self):
        self.assertFalse(RecordField.exists(self.testcoll, "newfield"))
        f = entitydata_recordfield_view_form_data(field_id="newfield", action="new")
        f['continuation_uri'] = ""
        u = entitydata_edit_uri("new", "testcoll", "_field", view_id="Field_view")
        r = self.client.post(u, f)
        # print r.content
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        self.assertEqual(r['location'], TestHostUri + entitydata_list_type_uri("testcoll", "_field"))
        # Check new entity data created
        self._check_view_data_values("newfield")
        return

    def test_post_new_field_cancel(self):
        self.assertFalse(RecordField.exists(self.testcoll, "newfield"))
        f = entitydata_recordfield_view_form_data(field_id="newfield", action="new", cancel="Cancel")
        u = entitydata_edit_uri("new", "testcoll", "_field", view_id="Field_view")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        self.assertEqual(r['location'], TestHostUri + entitydata_list_type_uri("testcoll", "_field"))
        # Check that new record type still does not exist
        self.assertFalse(RecordField.exists(self.testcoll, "newfield"))
        return

    def test_post_new_field_missing_id(self):
        f = entitydata_recordfield_view_form_data(action="new")
        u = entitydata_edit_uri("new", "testcoll", "_field", view_id="Field_view")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        self.assertContains(r, site_title("<title>%s</title>"))
        self.assertContains(r, "<h3>Problem with entity identifier</h3>")
        self.assertContains(r, "<h3>'_field' data in collection 'testcoll'</h3>")
        # Test context
        expect_context = entitydata_recordfield_view_context_data(action="new")
        self.assertDictionaryMatch(r.context, expect_context)
        return

    def test_post_new_field_invalid_id(self):
        f = entitydata_recordfield_view_form_data(field_id="!badfield", orig_id="orig_field_id", action="new")
        u = entitydata_edit_uri("new", "testcoll", "_field", view_id="Field_view")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        self.assertContains(r, site_title("<title>%s</title>"))
        self.assertContains(r, "<h3>Problem with entity identifier</h3>")
        self.assertContains(r, "<h3>'_field' data in collection 'testcoll'</h3>")
        # Test context
        expect_context = entitydata_recordfield_view_context_data(
            field_id="!badfield", orig_id="orig_field_id", action="new"
            )
        # log.info(repr(r.context['fields'][0]))
        self.assertDictionaryMatch(r.context, expect_context)
        return

    #   -------- copy type --------

    def test_post_copy_entity(self):
        self.assertFalse(RecordField.exists(self.testcoll, "copyfield"))
        f = entitydata_recordfield_view_form_data(field_id="copyfield", action="copy")
        u = entitydata_edit_uri("copy", "testcoll", 
            type_id="_field", view_id="Field_view", entity_id="Entity_type"
            )
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        self.assertEqual(r['location'], TestHostUri + entitydata_list_type_uri("testcoll", "_field"))
        # Check that new record type exists
        self._check_view_data_values("copyfield")
        return

    def test_post_copy_entity_cancel(self):
        self.assertFalse(RecordField.exists(self.testcoll, "copyfield"))
        f = entitydata_recordfield_view_form_data(field_id="copyfield", action="copy", cancel="Cancel")
        u = entitydata_edit_uri("copy", "testcoll", 
            type_id="_field", view_id="Field_view", entity_id="Entity_type"
            )
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        self.assertEqual(r['location'], TestHostUri + entitydata_list_type_uri("testcoll", "_field"))
        # Check that target record type still does not exist
        self.assertFalse(RecordField.exists(self.testcoll, "copyfield"))
        return

    def test_post_copy_entity_missing_id(self):
        f = entitydata_recordfield_view_form_data(action="copy")
        u = entitydata_edit_uri("copy", "testcoll", 
            type_id="_field", view_id="Field_view", entity_id="Entity_type"
            )
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        self.assertContains(r, site_title("<title>%s</title>"))
        self.assertContains(r, "<h3>Problem with entity identifier</h3>")
        self.assertContains(r, "<h3>'_field' data in collection 'testcoll'</h3>")
        expect_context = entitydata_recordfield_view_context_data(action="copy")
        self.assertDictionaryMatch(r.context, expect_context)
        return

    def test_post_copy_entity_invalid_id(self):
        f = entitydata_recordfield_view_form_data(
            field_id="!badentity", orig_id="orig_field_id", action="copy"
            )
        u = entitydata_edit_uri("copy", "testcoll", 
            type_id="_field", view_id="Field_view", entity_id="Entity_type"
            )
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        self.assertContains(r, site_title("<title>%s</title>"))
        self.assertContains(r, "<h3>Problem with entity identifier</h3>")
        self.assertContains(r, "<h3>'_field' data in collection 'testcoll'</h3>")
        expect_context = entitydata_recordfield_view_context_data(
            field_id="!badentity", orig_id="orig_field_id", action="copy"
            )
        self.assertDictionaryMatch(r.context, expect_context)
        return

    #   -------- edit type --------

    def test_post_edit_entity(self):
        self._create_view_data("editfield")
        self._check_view_data_values("editfield")
        f = entitydata_recordfield_view_form_data(
            field_id="editfield", action="edit", update="Updated entity"
            )
        u = entitydata_edit_uri("edit", "testcoll",
            type_id="_field", view_id="Field_view", entity_id="editfield"
            )
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        self.assertEqual(r['location'], TestHostUri + entitydata_list_type_uri("testcoll", "_field"))
        self._check_view_data_values("editfield", update="Updated entity")
        return

    def test_post_edit_entity_new_id(self):
        self._create_view_data("editfieldid1")
        self._check_view_data_values("editfieldid1")
        # Now post edit form submission with different values and new id
        f = entitydata_recordfield_view_form_data(
            field_id="editfieldid2", orig_id="editfieldid1", action="edit"
            )
        u = entitydata_edit_uri("edit", "testcoll", 
            type_id="_field", view_id="Field_view", entity_id="editfieldid1"
            )
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        self.assertEqual(r['location'], TestHostUri + entitydata_list_type_uri("testcoll", "_field"))
        # Check that new record type exists and old does not
        self.assertFalse(RecordField.exists(self.testcoll, "editfieldid1"))
        self._check_view_data_values("editfieldid2")
        return

    def test_post_edit_entity_cancel(self):
        self._create_view_data("editfield")
        self._check_view_data_values("editfield")
        # Post from cancelled edit form
        f = entitydata_recordfield_view_form_data(
            field_id="editfield", action="edit", cancel="Cancel", update="Updated entity"
            )
        u = entitydata_edit_uri("edit", "testcoll", 
            type_id="_field", view_id="Field_view", entity_id="editfield"
            )
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        self.assertEqual(r['location'], TestHostUri + entitydata_list_type_uri("testcoll", "_field"))
        # Check that target record type still does not exist and unchanged
        self._check_view_data_values("editfield")
        return

    def test_post_edit_entity_missing_id(self):
        self._create_view_data("editfield")
        self._check_view_data_values("editfield")
        # Form post with ID missing
        f = entitydata_recordfield_view_form_data(action="edit", update="Updated entity")
        u = entitydata_edit_uri("edit", "testcoll", 
            type_id="_field", view_id="Field_view", entity_id="editfield"
            )
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        self.assertContains(r, site_title("<title>%s</title>"))
        self.assertContains(r, "<h3>Problem with entity identifier</h3>")
        self.assertContains(r, "<h3>'_field' data in collection 'testcoll'</h3>")
        # Test context for re-rendered form
        expect_context = entitydata_recordfield_view_context_data(action="edit", update="Updated entity")
        self.assertDictionaryMatch(r.context, expect_context)
        # Check stored entity is unchanged
        self._check_view_data_values("editfield")
        return

    def test_post_edit_entity_invalid_id(self):
        self._create_view_data("editfield")
        self._check_view_data_values("editfield")
        # Form post with ID malformed
        f = entitydata_recordfield_view_form_data(
            field_id="!badfieldid", orig_id="orig_field_id", action="edit"
            )
        u = entitydata_edit_uri("edit", "testcoll", 
            type_id="_field", view_id="Field_view", entity_id="fieldid"
            )
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        self.assertContains(r, site_title("<title>%s</title>"))
        self.assertContains(r, "<h3>Problem with entity identifier</h3>")
        self.assertContains(r, "<h3>'_field' data in collection 'testcoll'</h3>")
        # Test context for re-rendered form
        expect_context = entitydata_recordfield_view_context_data(
            field_id="!badfieldid", orig_id="orig_field_id", action="edit"
            )
        self.assertDictionaryMatch(r.context, expect_context)
        # Check stored entity is unchanged
        self._check_view_data_values("editfield")
        return

# End.