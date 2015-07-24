"""
Tests for presenting multiple fields from referenced entity
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2014, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import sys
import os
import unittest
import re
from collections import OrderedDict

import logging
log = logging.getLogger(__name__)

from django.test.client                 import Client

from annalist.models.site               import Site
from annalist.models.collection         import Collection
from annalist.models.recordtype         import RecordType
from annalist.models.recordtypedata     import RecordTypeData
from annalist.models.recordview         import RecordView
from annalist.models.recordfield        import RecordField
from annalist.models.recordgroup        import RecordGroup
from annalist.models.entitydata         import EntityData

from tests                              import TestHost, TestHostUri, TestBasePath, TestBaseUri, TestBaseDir
from tests                              import init_annalist_test_site
from annalist.tests.AnnalistTestCase    import AnnalistTestCase
from entity_testutils               import (
    collection_create_values,
    create_test_user
    )
from entity_testtypedata            import (
    recordtype_create_values, 
    )
from entity_testentitydata          import (
    entity_url, entitydata_edit_url, 
    default_fields
    )

class RefMultifieldTest(AnnalistTestCase):

    def setUp(self):
        init_annalist_test_site()
        self.imagename = "test-image.jpg"
        self.imagepath = "%s/%s"%(TestBaseDir, self.imagename)
        self.imageuri  = "file://"+self.imagepath
        self.testsite  = Site(TestBaseUri, TestBaseDir)
        self.testcoll  = Collection.create(self.testsite,     "testcoll", collection_create_values("testcoll"))
        self.img_type  = RecordType.create(self.testcoll,     "img_type", recordtype_create_values("img_type"))
        self.img_data  = RecordTypeData.create(self.testcoll, "img_type", {})
        self.ref_type  = RecordType.create(self.testcoll,     "ref_type", recordtype_create_values("ref_type"))
        self.ref_data  = RecordTypeData.create(self.testcoll, "ref_type", {})
        # Login and permissions
        create_test_user(self.testcoll, "testuser", "testpassword")
        self.client = Client(HTTP_HOST=TestHost)
        loggedin    = self.client.login(username="testuser", password="testpassword")
        self.assertTrue(loggedin)
        return

    def tearDown(self):
        return

    # Support methods

    def _create_img_entity(self):
        # Create entity associated with uploaded image
        self.img_entity = EntityData.create(self.img_data, "img_entity",
            { "annal:type":         "test:img_type"
            , "rdfs:label":         "Label img_entity"
            , "rdfs:comment":       "Description of image"
            , "test:image":
                { 'upload_name':    "image_field"
                , 'resource_name':  "image_field.jpeg"
                , 'resource_type':  "image/jpeg"
                , 'uploaded_file':  self.imagename
                , 'uploaded_size':  1547926
                }
            })
        self.assertTrue(self.img_entity is not None)
        # Store image in entity directory
        img_fileobj = self.img_entity._fileobj(
            "image_field", "annal:Image", "image/jpeg", "wb"
            )
        with open(self.imagepath, "rb") as siteobj:
            img_fileobj.write(siteobj.read())
        img_fileobj.close()
        return self.img_entity

    def _create_ref_entity(self):
        ref_entity = EntityData.create(self.ref_data, "ref_entity",
            { "annal:type":         "test:ref_type"
            , "rdfs:label":         "Label ref_entity"
            , "rdfs:comment":       "Description of reference image record"
            , "test:ref_image":     "img_entity"
            })
        self.assertTrue(ref_entity is not None)
        return ref_entity

    def _create_refimg_view(self):
        refimg_view = RecordView.create(self.testcoll, "refimg_view",
            { 'annal:type':         "annal:View"
            , 'annal:uri':          "test:refimg_view"
            , 'rdfs:label':         "Test view label"
            , 'rdfs:comment':       "Test view comment"
            , 'annal:record_type':  "img_type"
            , 'annal:add_field':    True
            , 'annal:view_fields':
              [ { 'annal:field_id':         "Entity_id"
                , 'annal:field_placement':  "small:0,12;medium:0,6"
                }
              , { 'annal:field_id':         "refimg_field"
                , 'annal:field_placement':  "small:0,12;medium:0,6"
                }
              ]
            })
        self.assertTrue(refimg_view is not None)
        return refimg_view

    def _create_refimg_field(self, label_add=None, label_delete=None):
        refimg_field = RecordField.create(self.testcoll, "refimg_field",
            { "annal:type":                 "annal:Field"
            , "rdfs:label":                 "Image reference"
            , "rdfs:comment":               "Image reference field comment"
            , "annal:field_render_type":    "RefMultifield"
            , "annal:field_value_type":     "annal:Field_group"
            , "annal:field_entity_type":    "test:img_type"
            , "annal:placeholder":          "(ref image field)"
            , "annal:property_uri":         "test:ref_image"
            , "annal:field_placement":      "small:0,12;medium:0,6"
            , "annal:group_ref":            "test_refimg_group"
            , "annal:field_ref_type":       "img_type"
            })
        self.assertTrue(refimg_field is not None)
        return refimg_field

    def _create_refimg_group(self):
        test_refimg_group = RecordGroup.create(self.testcoll, "test_refimg_group",
            { "annal:type":         "annal:Field_group"
            , "annal:uri":          "test:test_refimg_group"
            , "rdfs:label":         "Ref image group label"
            , "rdfs:comment":       "Ref image group comment"
            , "annal:record_type":  "test:img_type"
            , "annal:group_fields": 
                [ { "annal:field_id":   "Test_comment" }
                , { "annal:field_id":   "Test_image"}
                ]
            })
        self.assertTrue(test_refimg_group is not None)
        return test_refimg_group

    def _create_refimg_image_field(self):
        test_refimg_image_field = RecordField.create(self.testcoll, "Test_image",
            {  "annal:type":                 "annal:Field"
            ,  "rdfs:label":                 "View image field"
            ,  "rdfs:comment":               "In view mode, displays an image."
            ,  "annal:field_render_type":    "RefImage"
            ,  "annal:field_value_type":     "annal:Image"
            ,  "annal:field_entity_type":    "test:img_type"
            ,  "annal:placeholder":          "(view image field)"
            ,  "annal:property_uri":         "test:image"
            ,  "annal:field_placement":      "small:0,12;medium:0,6"
            })
        return test_refimg_image_field

    def _create_refimg_comment_field(self):
        test_refimg_comment_field = RecordField.create(self.testcoll, "Test_comment",
            {  "annal:type":                 "annal:Field"
            ,  "rdfs:label":                 "View comment field"
            ,  "rdfs:comment":               "In view mode, displays a comment."
            ,  "annal:field_render_type":    "Markdown"
            ,  "annal:field_value_type":     "annal:Markdown"
            ,  "annal:field_entity_type":    "test:img_type"
            ,  "annal:placeholder":          "(view comment field)"
            ,  "annal:field_placement":      "small:0,12;medium:0,6"
            ,  "annal:property_uri":         "rdfs:comment"
            })
        return test_refimg_comment_field

    def _create_image_multifield_ref_and_view(self):
        # Create image entity with attached imagename
        img_entity = self._create_img_entity()
        # Create entity with reference to image entity
        ref_entity = self._create_ref_entity()
        # Create view of reference entity with multifield reference
        refimg_view = self._create_refimg_view()
        # Create multifield reference field
        refimg_field = self._create_refimg_field()
        # Create multifield reference group
        refimg_group = self._create_refimg_group()
        # Create multifield reference fields (where needed)
        refimg_image_field = self._create_refimg_image_field()
        refimg_image_field = self._create_refimg_comment_field()
        return

    # Tests

    def test_Ref_Multifield_view(self):
        self._create_image_multifield_ref_and_view()

        # Render view of multifield reference
        u = entitydata_edit_url("view", "testcoll", "ref_type", "ref_entity", view_id="refimg_view")
        r = self.client.get(u)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")

        # Check render context
        self.assertEqual(r.context['coll_id'],          "testcoll")
        self.assertEqual(r.context['type_id'],          "ref_type")
        self.assertEqual(r.context['entity_id'],        "ref_entity")
        self.assertEqual(r.context['action'],           "view")
        # Fields
        self.assertEqual(len(r.context['fields']), 2)
        # 1st field - Id
        self.assertEqual(r.context['fields'][0]['field_id'],            "Entity_id")
        self.assertEqual(r.context['fields'][0]['field_name'],          "entity_id")
        self.assertEqual(r.context['fields'][0]['field_label'],         "Id")
        self.assertEqual(r.context['fields'][0]['field_value'],         "ref_entity")
        # 2nd field - multifield group
        self.assertEqual(r.context['fields'][1]['field_id'],            "refimg_field")
        self.assertEqual(r.context['fields'][1]['field_name'],          "refimg_field")
        self.assertEqual(r.context['fields'][1]['field_label'],         "Image reference")
        self.assertEqual(r.context['fields'][1]['field_property_uri'],  "test:ref_image")
        self.assertEqual(r.context['fields'][1]['field_value_type'],    "annal:Field_group")
        self.assertEqual(r.context['fields'][1]['field_group_ref'],     "test_refimg_group")
        self.assertEqual(r.context['fields'][1]['group_label'],         "Image reference")
        self.assertEqual(r.context['fields'][1]['field_value'],         "img_entity")

        # Test rendered result
        field_vals    = default_fields(
            coll_id="testcoll", type_id="ref_type", entity_id="ref_entity", 
            view_id="refimg_view",
            basepath=TestBasePath
            )
        formrow1 = """
            <div class="small-12 medium-6 columns">
              <div class="row view-value-row">
                <div class="%(label_classes)s">
                  <span>Id</span>
                </div>
                <div class="%(input_classes)s">
                  <a href="%(basepath)s/c/%(coll_id)s/d/%(type_id)s/%(entity_id)s/?continuation_url=%(basepath)s/c/%(coll_id)s/v/%(view_id)s/%(type_id)s/%(entity_id)s/!view">%(entity_id)s</a>
                </div>
              </div>
            </div>
            """%field_vals(width=6)

        tgt_field_vals = default_fields(
            coll_id="testcoll", type_id="img_type", entity_id="img_entity", 
            view_id="refimg_view",
            field_id="image_field",
            basepath=TestBasePath
            )
        formrow2a = """
            <div class="small-12 medium-6 columns">
              <div class="row view-value-row">
                <div class="%(label_classes)s">
                  <span>View comment field</span>
                </div>
                <div class="%(input_classes)s">
                  <span class="markdown"><p>Description of image</p></span>
                </div>
              </div>
            </div>
            """%tgt_field_vals(width=6)
        formrow2b = (
            """<div class="small-12 medium-6 columns"> """+
              """<div class="row view-value-row"> """+
                """<div class="%(label_classes)s"> """+
                  """<span>View image field</span> """+
                """</div> """+
                """<div class="%(input_classes)s"> """+
                  """<a href="%(basepath)s/c/%(coll_id)s/d/%(type_id)s/%(entity_id)s/%(field_id)s.jpeg" target="_blank"> """+
                    """<img src="%(basepath)s/c/%(coll_id)s/d/%(type_id)s/%(entity_id)s/%(field_id)s.jpeg" """+
                    """     alt="Image at %(basepath)s/c/%(coll_id)s/d/%(type_id)s/%(entity_id)s/%(field_id)s.jpeg" /> """+
                  """</a> """+
                """</div> """+
              """</div> """+
            """</div> """
            )%tgt_field_vals(width=6)
        # log.info(r.content)
        self.assertContains(r, formrow1,  html=True)
        self.assertContains(r, formrow2a, html=True)
        self.assertContains(r, formrow2b, html=True)
        return

    def test_Ref_Multifield_edit(self):
        self._create_image_multifield_ref_and_view()

        # Render view of multifield reference
        u = entitydata_edit_url("edit", "testcoll", "ref_type", "ref_entity", view_id="refimg_view")
        r = self.client.get(u)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")

        # Check render context
        self.assertEqual(r.context['coll_id'],          "testcoll")
        self.assertEqual(r.context['type_id'],          "ref_type")
        self.assertEqual(r.context['entity_id'],        "ref_entity")
        self.assertEqual(r.context['action'],           "edit")
        # Fields
        self.assertEqual(len(r.context['fields']), 2)
        # 1st field - Id
        self.assertEqual(r.context['fields'][0]['field_id'],            "Entity_id")
        self.assertEqual(r.context['fields'][0]['field_name'],          "entity_id")
        self.assertEqual(r.context['fields'][0]['field_label'],         "Id")
        self.assertEqual(r.context['fields'][0]['field_value'],         "ref_entity")
        # 2nd field - multifield group
        self.assertEqual(r.context['fields'][1]['field_id'],            "refimg_field")
        self.assertEqual(r.context['fields'][1]['field_name'],          "refimg_field")
        self.assertEqual(r.context['fields'][1]['field_label'],         "Image reference")
        self.assertEqual(r.context['fields'][1]['field_property_uri'],  "test:ref_image")
        self.assertEqual(r.context['fields'][1]['field_value_type'],    "annal:Field_group")
        self.assertEqual(r.context['fields'][1]['field_group_ref'],     "test_refimg_group")
        self.assertEqual(r.context['fields'][1]['group_label'],         "Image reference")
        self.assertEqual(r.context['fields'][1]['field_value'],         "img_entity")

        # Test rendered result
        field_vals    = default_fields(
            coll_id="testcoll", type_id="ref_type", entity_id="ref_entity", 
            view_id="refimg_view",
            basepath=TestBasePath
            )
        formrow1 = """
            <div class="small-12 medium-6 columns">
              <div class="row view-value-row">
                <div class="%(label_classes)s">
                  <span>Id</span>
                </div>
                <div class="%(input_classes)s">
                  <input type="text" size="64" name="entity_id"
                         placeholder="(entity id)"
                         value="%(entity_id)s"/>
                </div>
              </div>
            </div>
            """%field_vals(width=6)

        tgt_field_vals = default_fields(
            coll_id="testcoll", type_id="img_type", entity_id="img_entity", 
            view_id="refimg_view",
            field_id="refimg_field",
            basepath=TestBasePath
            )
        formrow2 = """
            <div class="small-12 medium-6 columns">
              <div class="row view-value-row">
                <div class="%(label_classes)s">
                  <span>Image reference</span>
                </div>
                <div class="%(input_classes)s">
                  <div class="row">
                    <div class="small-10 columns view-value less-new-button">
                      <select name="%(field_id)s">
                       <option selected="selected">%(entity_id)s</option>
                      </select>
                    </div>
                    <div class="small-2 columns view-value new-button left small-text-right">
                      <button type="submit"
                              name="%(field_id)s__new"
                              value="New"
                              title="Define new Image reference"
                      >
                        +
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            """%tgt_field_vals(width=6)

        # log.info(r.content)
        self.assertContains(r, formrow1,  html=True)
        self.assertContains(r, formrow2,  html=True)
        return

# End.

if __name__ == "__main__":
    # import django
    # django.setup()  # Needed for template loader
    # Runtests in this module
    # runner = unittest.TextTestRunner(verbosity=2)
    # tests = unittest.TestSuite()
    # tests  = getSuite(select=sel)
    # if tests: runner.run(tests)
    unittest.main()