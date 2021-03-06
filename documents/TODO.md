# Annalist TODO

NOTE: this document is used for short-term working notes; some longer-term planning information has been migrated to [Github issues](https://github.com/gklyne/annalist/issues) and a [roadmap document](roadmap.md).


# Documentation

- [ ] Add documentation for view Type, View, List and Group forms (similar to view Field ...)
- [ ] HOWTOs for common tasks; task-oriented documentation
    - Have tutorial; can this be used?
- [ ] Update tutorial to cover inheritance of definitions
- [ ] Review concurrent access issues; document assumptions
    - original design called for copy of original record data to be held in form, so that changes could be detected when saving entity; also, allows for "Reset" option.
- [ ] New demo screencasts


# Version 0.1.31, towards 0.1.32

- [x] annalist-manager config directory - display directory where config setting files are located
    - e.g. anenv/lib/python2.7/site-packages/annalist_root/annalist_site/settings/
    - (same as SITE_CONFIG_DIR in log)
- [x] Entity types list (and List list?) - provide link field to display list
- [x] Entity lists - set state of scope all checkbox to reflect scope parameter
- [x] Help text for 'Customize' display
    - This is taken from the collection metadata.
- [x] Fix behaviour of collection inheritance - data not inherited?
    - Note that the search logic has reduced test suite performance by 10-15%
    - may want to look later for optimizations here (e.g. cache collection data).
- [x] Establish collection as base URI for Markdown text links, or provide some kind of prefix expansion.
    - relative references are unreliable 
    - views/displayinfo.py, context_data is key function for assembling context info
    - substitution syntax:  $name, $name:, $[CURIE], $$ -> $, else as-is
    - Name characters are ALPHA, DIGIT, "_"
    - CURIE characters for subsitution: name characters, plus:
      "@", ".", "~", "-", "+", "*", "=", ":", ";", ",", "/", "?", "#", "!"
    - [x] add site_base_url (SITE), coll_base_url (COLL) and site_host_name (HOST) to context
    - [x] add BASE to context: path for relative reference of collection entities (including `/d/`).
    - [x] define substitution function in displayinfo
    - [x] apply substitutions when setting help_markdown (displayinfo.context_data())
    - [x] apply substitutions in views/fields/render_text_markdown.py text_markdown_view_renderer.render
    - [x] test case (markdown renderer)
    - [x] documentation (markdown field render type)
    - [x] use substitutions in help text
    - [x] add link to markdown field render type in help fields using Markdown
    - [x] User view description field - add "markdown" text.
    - [x] Use $BASE substitutions in help text for installable collections
- [x] Rethink field padding model
    - Generate columns explicitly within rows, not assuming they will just flow.
    - All field lists are processed through FieldListValueMap
    - Each field is handled by a referenced FieldValueMap instance
    - [x] Define new class FieldRowValueMap
    - [x] Define renderer for field row that wraps list of fields as a row
    - [x] Re-work FieldListValueMap to break fields into rows and call FieldRowValueMap with each such group
    - [x] Check and fix test cases
- [x] Login window: implement "Local" as a provider, authenticated against the local Django user base.
    - [x] Gereralize default proider mechanism, make "Google" default provider
    - [x] Local login: use userid from login front page, if defined
    - [x] Local login redirects to login form - should display profile
    - [x] Retain userid on login front page after login failure
    - [x] Use buttons on login form instead of (or as well as) dropdown
    - [x] Profile display accept POST and redirect to continuation
    - [x] Save recent user id in session to facilitate login
    - [x] Allow blank user id and construct value from authenticated email
    - [x] Use button label from provider details (else provider name)
    - [x] Login/Logout/profile buttons to include continuation
    - [x] Login form cancel button: return to continuation URL
    - [x] Local login continuation not applied (cancel is OK)
    - [x] Fix tests
    - [x] Modularize and clean up duplicate code 
    - [x] Login messages to separate module for ease of translation
- [x] Rationalize login provider details handling
    - [x] Obtain scope from provider details
    - [x] Save entire provider detail in request.session - access values from there
- [x] annalist-manager site data initialization: 
    - copy local id provider and examples to site config
- [x] Login/logout: support continuation URI
- [x] Make login screen clearer (cf. email from Iris 06/10/2015 16:15) 
    - [x] the role of the user Id field is not clear; Iris tried password there
    - [x] if id is left blank, use email local part (with substitutions)
- [x] New logins: automatically create new user record with default permissions.
- [x] Fix bug in display of entity lists from `_annalist_site` collection
- [x] Check out context definition conflict for list (cf. rdfs:seeAlso)
    - [x] Add test case for vocabulary view
    - [x] Add logic to generate set context for seeAlso
    - [x] Update all existing site data references to "RepeatGroup" and "RepeatGroupRow"
    - [x] Update site data and tests to use type-qualified render type and value mode values.
    - [x] Add migration logic for field definitions to use new render type names.
- [x] Changed "field value type" in field description for repeat/multifield reference fields to indicate
    the type of the referenced group, or if it contains a singleton the referenced target value type.
    These changes affect data rather than fundamental workings of Annalist; the tasks for creating
    repeat fields and multifield references have been updated.
- [x] Refactor context checking for field lists (`test_entitygenericlist`, `test_entityinheritlist`)
- [x] Migration options for references to `Field_render` and `Field_type` in views, groups and lists
- [x] Use "@base" declaration in entities
    - [x] Each entity/record type to declare a reference to base container URI
    - [x] Context file in base container
    - [x] Replace `_contextref` with `_baseref`
    - [x] For RecordEnum, use different reference to base directory so '_annalist_collection/' or 'd/' is accessed as context directory.  
    - [x] Don't generate enums/coll_context.lsonld.  Update context references in Enum values.
    - [x] Add base declaration to entity files, etc.
    - [x] Generate entity IDs relative to collection base directory
        - There's still some ad-hocery around handling of references to enumerated values.
        - See actions below to review URI and directrory usage.
    - NOTES:
        - `@base` ignored if used in external contexts;
        - `@base` can specified value be relative? YES:
            - [syntax sect 8.7](http://www.w3.org/TR/json-ld/#context-definitions) and 
            - [API sect 6.1](http://www.w3.org/TR/json-ld-api/#context-processing-algorithm) para 3.4
        - BUT: rdflib-jsonld implementation currently ignores `@base` when accessing an external context resource.
        - Use `(site_base)/c/(coll_id)/d/` as base URI so that entity ids (`type_id/entity_id`) work directly as relative references.  
        - Also `type_id` to retreive a list of entities of that type.
        - Thus use `{ "@base": "../..", @context": "@context", ... }` in entity data.
        - previously, there was a problem with rdflib-jsonld base URI handling.
            - cf. https://github.com/RDFLib/rdflib-jsonld/issues/33
- [x] BUG: JSON URI wrong in JSON-LD output? e.g. 
    "http://fast-project.annalist.net/annalist/c/Performances/d/Ensemble/Phil_Langran_band/Musician/Phil_Langran"
    shoud be: "http://fast-project.annalist.net/annalist/c/Performances/d/Musician/Phil_Langran/
    - [x] Change entity references (select rendered) to @type @id in context
        - cf. models.collection.get_coll_jsonld_context, etc.
    - [x] Rename directories used for built-in types to match type name
        - views.collection -> annalist.models.collectiondata.migrate_coll_data
        - am_managecollections -> annalist.models.collectiondata.migrate_coll_data
        - collection object is parameter
        - [x] Add new, old directory names to layout.py
        - [x] Find all references to directory names, use layout symbols
        - [x] Add function in collectiondata to rename directories
        - [x] Add call to directory migration function in collection view method from site
        - [x] Add call to directory migration function in collectiondata.migrate_coll_data
        - [x] Rename directories in sitedata in source tree and layout.
- [x] Fix bug in list search function: not finding values in repeated groups

(Release?)

- [ ] BUG: login button images not copied to new installation.
- [ ] BUG: Site users removed by software update (confirmed).
- [ ] README front page and PyPI front page include pointer to annalist.net
- [ ] If logout results in loss of authorization to view resource, go to collection view
- [ ] Review file/URL layout for enums, etc 
    - (Enums?  For web access or file access?)
    - (<type_id>/<entity_id>: e.g. d/Enum_value_mode/Value_direct/)
    - need to make sure that access isn't interrupted by URI/FILE path discrepancies; e.g. Enum
    - consider: use of file:// URI vs http://.  Need data to work without Annalist present.
    - thus need consistency.  Use d/_enum/Enum-type/value for now?
- [ ] Remove surplus fields from context when context generation/migration issues are settled
    - cf. collection.set_field_uri_jsonld_context, collection.get_coll_jsonld_context (fid, vid, gid, etc.)
- [ ] Replace print statements in data migration code with a proper reporting/diagnostic mechanism.
- [ ] Task button option to copy type+view+list and update names and URIs
- [ ] Review URI usage
    - [ ] separation of collection metadata and entity data is a bit messy.  Could we drop the `/d/` segment and just use type names (and maybe a reserved directory for collection metadata)?
        - note extra logic in models.collectiondata and models.entitytypeinfo, etc.
        - this would also simplify the base URI issues, and reduce the duplication of JSON-LD context files.
    - [x] avoid explicit reference to `_annalist_collection`?
    - [x] collections and repeated properties:
        - Using owl:sameAs in form { "owl:sameAs": <some_resource> } as equivalent to just <someresource>.
        - Use `@id`, thus: { "@id": <some_resource> } .
- [ ] Access to page link without continuation (view only)?
- [ ] Review length restriction on entity/type ids: does it serve any purpose?

- [ ] Easy way to view log; from command line (via annalist-manager); from web site (link somewhere)
    - [x] annalist-manager serverlog command returns log file name
    - [ ] site link to download log, if admin permissions (could be a data bridge?)
    - [ ] rotate log files (max 5Mb?) (cf. [RotatingFileHandler](https://docs.python.org/2/library/logging.handlers.html#logging.handlers.RotatingFileHandler))
- [ ] annalist-manager options for users, consider:
    - [ ] annalist-manager createlocaluser [ username [ email [ firstname [ lastname ] ] ] ] [ CONFIG ]
    - [ ] annalist-manager setuserpermissions [ username [ permissions ] ] [ CONFIG ]
- [ ] `annal:Slug` type URI for entity references - is now type/id: rename type?  (annal:Entity_ref?)
    - include migration logic

(feature freeze for V0.9alpha?)
(0.5?)

- [ ] TECHDEBT: render modes:  instead of a separate function for each mode, pass parameter to each renderer and select at the point of rendering (e.g. see render_fieldvalue.render_mode) - this should avoid the need for the multiple layers of wrapping and duplication of render mode functions.  Field description should carry just a single renderer; figure later what to do with it.)
- [ ] *delete views: rationalize into single view?
- [ ] performance tuning: in EntityTypeInfo: cache type hierarchy for each collection/request; clear when setting up
- [ ] look into entity cacheing (esp. RecordType) for performance improvement
- [ ] update Django version used to latest version designated for long term support (1.8?)
- [ ] review renderers and revise to take all message strings from messages.py
- [ ] review title/heading strings and revise to take all message strings from messages.py
- [ ] entityedit view handling: view does not return data entry form values, which can require some special-case handling.  Look into handling special cases in one place (e.g. setting up copies of form values used but not returned.  Currently exhibits as special handling needed for use_view response handling.)
- [ ] Review nomenclature, especially labels, for all site data
- [ ] Eliminate type-specific render types (i.e. 'Type', 'View', 'List', 'Field', etc.), and any other redundant render types.  Also "RepeatGroup" and "RepeatGroupRow".  Also "Slug"?
- [ ] Provide content for the links in the page footer
- [ ] Security and robust deployability enhancements [#12](https://github.com/gklyne/annalist/issues/12)
    - [ ] deploy `letsencrypt` certs on all `annalist.net` servers and foce use of HTTPS.
        - [ ] Document setup process.
    - [ ] Check out https://docs.djangoproject.com/en/1.8/ref/django-admin/#django-admin-check
    - [ ] Shared/personal deployment should generate a new secret key in settings
    - [ ] Need way to cleanly shut down server processes (annalist-manager option?)
    - [ ] See if annalist-manager runserver can run service directly, rather than via manage.py/django-admin?
- [x] Remove dependency of annalist-manager on test-suite-generated data when creating/updating site
    - copy site data in directly from `sitedata`
    - generate all other site data on-the-fly as needed (e.g. context, etc.)
- [ ] Figure out how to preserve defined users when reinstalling the software.
    - I think it is because the Django sqlite database file is replaced.  Arranging for per-configuration database files (per above) might alleviate this.
    - Seems to be working, but needs explicit testing to make sure.
- [ ] Automated test suite for annalist_manager
    - [ ] annalist-manager initialize [ CONFIG ]
    - [ ] annalist-manager createadminuser [ username [ email [ firstname [ lastname ] ] ] ] [ CONFIG ]
    - [ ] annalist-manager updateadminuser [ username ] [ CONFIG ]
    - [ ] annalist-manager setdefaultpermissions [ permissions ] [ CONFIG ]
    - [ ] annalist-manager setpublicpermissions [ permissions ] [ CONFIG ]
    - [ ] annalist-manager deleteuser [ username ] [ CONFIG ]
    - [ ] annalist-manager createsitedata [ CONFIG ]
    - [ ] annalist-manager updatesitedata [ CONFIG ]
    - etc.
- [ ] Review docker files: reduce number of separate commands used; always build on clean python setup
- [ ] Code and service review  [#1](https://github.com/gklyne/annalist/issues/1)
- [ ] Simplify generic view tests [#33](https://github.com/gklyne/annalist/issues/33)
- [ ] Checkout default form buttons. See:  http://stackoverflow.com/questions/1963245/multiple-submit-buttons-on-html-form-designate-one-button-as-default/1963305#comment51736986_1963305
- [ ] Move outstanding TODOs to GitHub issues

Data collection definitions:

- [ ] VoID, DCAT


Technical debt:

- [ ] Implement in-memory entity storage to speed up test suite, and lay groundwork for LDP back-end
- [ ] Move top menu selection/formatting logic from template into code (e.g. context returned by DisplaytInfo?)
- [ ] Rework Bib_* definitions/enumerations so that they don't need special mention in EntityInfo
- [ ] Consider treating Enum types as regular types under /d/?
- [ ] Field layout padding logic at end of row is dependent on height of edit fields; consider re-working this in `fieldlistvaluemap` to generate fields in groups, where each group is rendered as a separate row.
- [ ] Built-in type id's: use definitions from `models.entitytypeinfo` rather than literal strings
- [ ] Consider `views.site`, `views.collection` refactor to use `views.displayinfo`
- [ ] Implement "get the data" link as a field renderer?
- [ ] Consider eliminating the /c/ directory (but provide redirects for link compatibility/coolness)
- [ ] review view URL returned for entities found with alternative parentage:
    - currently force URL returned to be that of original parent, not alt. 
    - This is done to minimize disruption to tests while changing logic.
    - See: _entityviewurl member variable
    - logic is handled in `Entity.try_alt_parentage` and _init_child`
    - may want to consider promoting entityviewurl to constructor parameter for all Entity.
- [ ] Delay accessing settings data until actually needed, so that new dependencies (e.g. models on views) don't cause premature selection.  This will help to avoid certain unexpected problems cropping up as happened with release 0.1.22 logging setup for annalist-manager.
- [ ] After reworking site data access, review `layout.py` and patterns for accessing entities, metadata, context data, etc.
    - The various relative references for accessing context data are particularly unclear in the current software.
- [ ] Inconsistent `@id` values in site data
- [ ] Re-think access to entities and types:
    - [ ] There is repeated reading of RecordType values in EntityFinder
          (cf. collection.types() and EntityTypeInfo constructor; also URI access)
    - [ ] Need more direct way to locate type (and other entities?) by URI
    - [ ] Review common mechanism to retreive URI for entity?  
          (Current mechanism fixes use of annal:uri for all entities; maybe OK)
    - [ ] Think about how to optimize retreival of subtypes/supertypes
    - [ ] Do special case for types, or more generic caching approach?
- [ ] Customize view style getting out of sync with other page styles
    - possible enhancements to form generator to generate customize page using form logic?
- [ ] Refactor entity edit response handling
- [ ] Review handling of composite type+entity identifiers in list display selections to bring in line with mechanisms used for drop-down choicess.
- [ ] In render_select.py: remove references to {{field.field_value}} and {{field.field_value_link_continuation}} and use locally generated {{field_labelval}}, etc.
    - [ ] The continuation URI will need to be provided separately in the context (via bound_field?) and mentioned separately in the templates.
    - [ ] Remove corresponding special case code in bound_field.
- [x] The field rendering logic is getting a bit tangled, mainly due to support for uploaded files and multiple field references to a linked entity.  Rethinking this to maintain a clearer separation between "edit" and "view" modes (i.e. separate render classes for each) should rationalize this.  The different modes require multiple methods on different modules in different classes;  can the field description have just 2 renderer references (read/edit) and handle the different modes from there?  (It is field description values that are referenced from templates.)
- [ ] The handling of entity_id and entity_type involves some special case testing in bound_field, due somewhat to the early template-based logic for field rendering.  With the introduction of separate render-templates in views.fields.render_select.py, it may be possible to change the context variables used for this case and remove the special logic in bound_field.
- [ ] Similar to above for entity_id, except that it uses a separate template in templates.fields.
- [ ] Can annal:field_name in field descriptions be eliminated with revised entity_id and entity_type logic?
- [ ] Check EntityId and EntityTypeId renderers appear only at top-level in entity view


Usability notes:

- [ ] Absorb groups into field defs?
- [ ] Add menu bar link to display content of collection rather than default
    - List of types, linked to lists?
- [ ] Try to make changing entity type and entity id follow-through more smoothly.
    - especially when creating a supertype and selecting an appropriate subtype.
- [ ] Better support for type renaming: hunt out all references and rename them too
- [ ] Consistency checks for references to missing types (e.g. following rename)
- [x] Display entity-id *and* label values in drop-downs?  (e.g. "id (label)")
- [ ] Simplified field-definition interface? (hide confusing detail; use javascript to hide/expose fields based on selection from simple enumeration of field types?)
- [ ] Persist item selection to refreshed display when move-up/movedown clicked?
- [x] Easy(er) switch to alternative views (e.g. manufacture, performance for Carolan events)
- [x] OR... allow an entity to specify its own default view? (this is now handled by subtyping)
- [ ] Type/List/View dropdowns: normally show only those types/lists/views defined by the current collection, but ensure it is still reasonably easy to get lists of built-in types as well.  Details need to be worked out.
- [x] View forms need title (indicating type of thing viewed)?  Or let user define label for Id field?
- [x] Provide field type that can be used to place fixed annotations/instructions in a form
- [ ] Introduce notion of "Task", based on form, but linked to "script" action.
    - [x] Create a "wizard-like" (or one-form) interface for creating type+list+view set.
        - test by creating contacts/supplies list for CruisingLog
    - [x] Create a "wizard-like" (or one-form) interface for creating field+field-group set.
        - needs to create (a) individual fields in group, (b) field group and (c) field referring to group.
    - [ ] Create a "wizard-like" (or one-form) interface for creating subtype+view+list from existing type
    - [ ] Procedure for creating type + view definition + list definition + field definitions from a simple overview description
    - [ ] Procedure for creating enumeration type from simple description of options
    - [ ] Procedure to migrate textual type annotations to enumeration types
    - [ ] Renderer for generating back-links to records that reference the current record
    - [ ] Simplify repetitive data entry; e.g.
        - Use-case: create bibliographic author details from just full name entered
        - [ ] derived field (possibly hidden) with a rule to guide its creation from other fields in a view
        - [ ] default value from other field (possibly from a derived field)
        - [ ] initial value/identifier templates (e.g. create ID from current date)
            - NOTE: default and initial values behave differently
        - [ ] "view source" record editing (of JSON), with post-entry syntax checking.
- [ ] Getting type URI/CURIE to match across type/list is too fragile.  Avoid using selector for this unless it's really needed?  In particular, getting the entity type for a field is error-prone.
- [x] Option to re-order fields on view form
- [ ] When creating type, default URI to be based on id entered
- [ ] List display paging
- [ ] When generating a view of an enumerated value, push logic for finding link into the renderer, so that availability of field link does not depend on whether field is available for the selected view.  (Try changing entity type of field to random value - can no longer browse to field description from view/group description)


Notes for Future TODOs:

(Collecting ideas here: consider expand them in the GitHub issues list.)

- [ ] Review how URIs are generated for referenced entities: currently a relative reference is used, which resolves to a local URL for the entity concerned.  But if the entity has a global identifier (`annal:URI`) that that should appear in exported data.  One fix is to just use global URIs in text fields when global URIs are expected (e.g. supertypes in class description).  E.g., consider generating:
    "rdfs:subClassOf": [
      { "@id": "Class/Resource", "owl:sameAs": "rdfs:Resource"}
      ]
    - annal:display_type values (List/Grid) are another example to consider.
- [ ] Field option to display item(s) in list (e.g. domain).
    - Generalize to path in list objects?
    - cf. https://tools.ietf.org/html/rfc6901 (JSON pointer)
- [ ] Keyboard shortcuts on forms - C-S to save, ...?
- [ ] Implement at least one other identify provider (ORCID?)
    - [ ] ORCID authentication - apparently OAuth2 based (cf. contact at JISC RDS workshop).  
        - See also http://support.orcid.org/forums/175591-orcid-ideas-forum/suggestions/6478669-provide-authentication-with-openid-connect
    - [ ] Other OpenID Connect providers; e.g. see http://openid.net/certification/
        - hard to find actual provider service other than Google
- [ ] Think about facility to make it easier to create identity provider details.  (?)
- [ ] Views providing different perspectives on data; e.g. artifact centres, event centred, etc.  Would need a way to find inbound references as well as outbound.
- [ ] Generate default value type for field based on render type + value mode (to help with consistency)
    - See notes.
- [ ] It would be nice if link field tooltips describe what they link to.
- [ ] Rethink collection overview that allows users to see what is present
    - original thoughts, but review in light of default-view approach adopted:
        - initially, just provide a "What's here" list that displays default list label for all types + link to display list.
        - think about an item list renderer (what is variable?)
        - longer term, this might be a high-level graphical display (like PROV diag.)
        - use this to think about linking to alternative displays
- [ ] Extend/alternative view-text field to combine data from multiple fields (per template)
- [ ] From view of list definition, link to show list itself
    - Beside "Show view" button, add "Show list"?
    - tried investigating EUDat, which looks promising but fails with invalid certificate

- [ ] Embedded code expansion in help text, and maybe other Markdown:
    - [ ] {{site}} base URL for site
    - [ ] {{coll}} base url for collection
    - [ ] {{url:typeid/entityid}} UREL for referenced entity.
    - [ ] {{ref:typeid/entityid}} link for referenced entity, using label from target.
    - [ ] {{field:typeid/entityid#property_uri}} field from referenced entity

- [ ] Think about how to incorporate resources from other collections by reference: feed into data bridges?

- [ ] Think about extending field descrtiptions to include:
    - [ ] superproperty URIs (similar to supertype URIs in types)
    - [ ] rules that allow inferences of multiple RDF statements; e.g.
        ?a isRecordingOf ?b
        => 
        [ a frbroo:F29_Recording_Event ]
            frbroo:R20F_recorded ?b ;
            frbroo:R21F_created ?a .
    - the above pair might be combined.  We would then want to run the inferences when exporting JSON-LD
- [ ] Collection metadata editing requires site-level permissions; 
    - to apply collection level permissions wout require entity level access control settings
    - think about this?
    - see EntityTypeInfo.__init__
- [ ] Introduce site-local and/or collection-local CSS to facilitate upgrades with local CSS adaptations.
- [ ] Issues raised by Cerys in email of 23-Oct-2015.  Some good points there - should break out into issues.
- [ ] consider render type option for repeat group rows without headings? (simple repeat group doesn't hack it).
    - Should be easy to add.  Just need a name.
- [ ] Scrolling through views from list - e.g. Next/Prev item buttons? (Iris G)
- [ ] Option to scan for broken entity references (e.g., due to removal, renaming)
- [ ] Extend task definitions to include validation: allow error reporting
- [ ] Allow comment field to be left blank and use label instead?  Maybe not: later, allow comment field to default to label.
- [ ] field renderer for unified import or upload resource?
- [ ] Improve reporting of errors due to invalid view/field definitions, etc.
- [ ] add 404 handling logic to generate message and return to next continuation up the chain.
    - [ ] reinstate get_entity_data in displayinfo, and include 404 response logic.
    - [ ] update entityedit c.line_116 to use new displayinfo function.  This will mean that all 404 response logic is concentrated in the displayinfo module. (Apart from statichack.)
    - [ ] update displayinfo so that it receives a copy of the continuation data when initialized.
    - [ ] pass continuation data into view_setup, list_setup, collection_view_setup for ^^.  For site, just use default/empty continuation.
    - [ ] Calling sites to collect continuation are: EntityGenericListView.get, EntityGenericListView.post, EntityDeleteConfirmedBaseView.complete_remove_entity, GenericEntityEditView.get, GenericEntityEditView.post.
- [ ] Image collections - check out http://iiif.io/, http://showcase.iiif.io/, https://github.com/pulibrary/loris
- [ ] Review field placement and layout grid density (16col instead of 12col?)
- [ ] Rationalize common fields to reduce duplication?
    - but note that fields may use different comment/help text, so maybe not.
- [ ] introduce general validity checking framework to entityvaluemap structures (cf. unique property URI check in views) - allow specific validity check(s) to be associated with view(s)?  But note that general philosophy is to avoid unnecessary validity checks that might impede data entry.
- [ ] New field renderer for displaying/selecting/entering type URIs, using scan of type definitions.
- [ ] Make default values smarter; e.g. field renderer logic to scan collection data for candidates?
- [ ] Allow type definition to include template for new id, e.g. based on current date
- [ ] Use local prefix for type URI (when prefixes are handled properly); e.g. coll:Type/<id>
- [ ] Associate a prefix with a collection? 
- [x] Provide a way to edit collection metadata (e.g. link from Customize page)
- [x] Provide a way to edit site metadata (e.g. via link from site front page)
- [ ] Provide a way to view/edit site user permissions (e.g. via link from site front page)
- [x] Provide a way to view/edit site type/view/list/etc descriptions (e.g. via link from site front page)
    - not edit: site data should be stable and controlled.  Consider collection structure inheritiance instead.
- [ ] Undefined list error display, or any error - include link to collection in top bar
- [x] Help display for view: use commentary text from view description; thus can tailor help for each view.
- [ ] Use markdown directly for help text
- [ ] Think about fields that return subgraph
    - how to splice subgraph into parent - "lambda nodes"?
    - does field API support this? Check.
    - cf. [JSON-LD framing](http://json-ld.org/spec/latest/json-ld-framing/)
- [ ] For rendering of additional info, think about template-based URIs filled in from other data.  (e.g. URI to pull an image from CLAROS, or Google graph API like)
- [ ] Generate form-level DIFF displays from git JSON diffs
- [ ] 3D rendering - check out JSMOL - http://wiki.jmol.org/index.php/JSmol
- [ ] Visualize data structures from view definitions; generate OWL descriptions; etc.
- [ ] Remixing spreadsheets: spreadsheet generation from queries as well as ingesting through data bridges.
- [ ] SPARQL data bridge: use combination of SPARQL CONSTRUCT query + JSON-LD frame?
- [ ] View selection based on pattern match; e.g. JSON PATCH "Test" operation.
- [ ] git/github integration
    - [ ] annalist-manager options to load/save collection using git (assuming git is installed)
    - [ ] internal options to save history in per-collection git repo


# Feedback

* https://github.com/gklyne/annalist/issues/40


----
