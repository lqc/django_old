# -*- coding: utf-8 -*-
import datetime

from django.core.files.uploadedfile import SimpleUploadedFile
from django.forms import *
from django import forms
from django.http import QueryDict
from django.template import Template, Context
from django.utils.datastructures import MultiValueDict, MergeDict
from django.utils.safestring import mark_safe
from django.utils.unittest import TestCase


class PersonWithoutFormfields(Form):
    first_name = CharField()
    last_name = CharField()
    birthday = DateField()
    band = CharField()
    secret = CharField(widget=HiddenInput)

class Person(PersonWithoutFormfields):
    class Meta:
        fieldsets = (
            (None, {
                'fields': ('first_name', 'last_name', 'birthday'),
            }),
            ("Additional fields", {
                'fields': ('band', 'secret'),
            }),
        )

class FieldsetsTestCase(TestCase):

    some_data = {
        'first_name': u'John',
        'last_name': u'Lennon',
        'birthday': u'1940-10-9',
        'band': u'The Beatles', 
        'secret': u'he didnt say',
    }

    def test_simple_rendering(self):
        # Pass a dictionary to a Form's __init__().
        p = Person(self.some_data)
        # as_table
        self.assertEqual(str(p), """<fieldset>
<table>
<tr><th><label for="id_first_name">First name:</label></th><td><input type="text" name="first_name" value="John" id="id_first_name" /></td></tr>
<tr><th><label for="id_last_name">Last name:</label></th><td><input type="text" name="last_name" value="Lennon" id="id_last_name" /></td></tr>
<tr><th><label for="id_birthday">Birthday:</label></th><td><input type="text" name="birthday" value="1940-10-9" id="id_birthday" /></td></tr>
</table>
</fieldset>
<fieldset>
<legend>Additional fields</legend>
<table>
<tr><th><label for="id_band">Band:</label></th><td><input type="text" name="band" value="The Beatles" id="id_band" /><input type="hidden" name="secret" value="he didnt say" id="id_secret" /></td></tr>
</table>
</fieldset>""")
        self.assertEqual(str(p), unicode(p))
        self.assertEqual(str(p), p.as_table())
        # as_ul
        self.assertEqual(p.as_ul(), """<fieldset>
<ul>
<li><label for="id_first_name">First name:</label> <input type="text" name="first_name" value="John" id="id_first_name" /></li>
<li><label for="id_last_name">Last name:</label> <input type="text" name="last_name" value="Lennon" id="id_last_name" /></li>
<li><label for="id_birthday">Birthday:</label> <input type="text" name="birthday" value="1940-10-9" id="id_birthday" /></li>
</ul>
</fieldset>
<fieldset>
<legend>Additional fields</legend>
<ul>
<li><label for="id_band">Band:</label> <input type="text" name="band" value="The Beatles" id="id_band" /><input type="hidden" name="secret" value="he didnt say" id="id_secret" /></li>
</ul>
</fieldset>""")
        # as_p
        self.assertEqual(p.as_p(), """<fieldset>

<p><label for="id_first_name">First name:</label> <input type="text" name="first_name" value="John" id="id_first_name" /></p>
<p><label for="id_last_name">Last name:</label> <input type="text" name="last_name" value="Lennon" id="id_last_name" /></p>
<p><label for="id_birthday">Birthday:</label> <input type="text" name="birthday" value="1940-10-9" id="id_birthday" /></p>

</fieldset>
<fieldset>
<legend>Additional fields</legend>

<p><label for="id_band">Band:</label> <input type="text" name="band" value="The Beatles" id="id_band" /><input type="hidden" name="secret" value="he didnt say" id="id_secret" /></p>

</fieldset>""") # Additional blank lines are ok

    def test_single_fieldset_rendering(self):
        # Pass a dictionary to a Form's __init__().
        p = Person(self.some_data)
        # as_table
        self.assertEqual(str(p.fieldsets[0]), """<tr><th><label for="id_first_name">First name:</label></th><td><input type="text" name="first_name" value="John" id="id_first_name" /></td></tr>
<tr><th><label for="id_last_name">Last name:</label></th><td><input type="text" name="last_name" value="Lennon" id="id_last_name" /></td></tr>
<tr><th><label for="id_birthday">Birthday:</label></th><td><input type="text" name="birthday" value="1940-10-9" id="id_birthday" /></td></tr>""")
        self.assertEqual(str(p.fieldsets[0]), unicode(p.fieldsets[0]))
        self.assertEqual(str(p.fieldsets[0]), p.fieldsets[0].as_table())
        self.assertEqual(str(p.fieldsets[1]), """<tr><th><label for="id_band">Band:</label></th><td><input type="text" name="band" value="The Beatles" id="id_band" /><input type="hidden" name="secret" value="he didnt say" id="id_secret" /></td></tr>""")
        self.assertEqual(str(p.fieldsets[1]), p.fieldsets[1].as_table())
        # as_ul
        self.assertEqual(p.fieldsets[0].as_ul(), """<li><label for="id_first_name">First name:</label> <input type="text" name="first_name" value="John" id="id_first_name" /></li>
<li><label for="id_last_name">Last name:</label> <input type="text" name="last_name" value="Lennon" id="id_last_name" /></li>
<li><label for="id_birthday">Birthday:</label> <input type="text" name="birthday" value="1940-10-9" id="id_birthday" /></li>""")
        self.assertEqual(p.fieldsets[1].as_ul(), """<li><label for="id_band">Band:</label> <input type="text" name="band" value="The Beatles" id="id_band" /><input type="hidden" name="secret" value="he didnt say" id="id_secret" /></li>""")
        # as_p
        self.assertEqual(p.fieldsets[0].as_p(), """<p><label for="id_first_name">First name:</label> <input type="text" name="first_name" value="John" id="id_first_name" /></p>
<p><label for="id_last_name">Last name:</label> <input type="text" name="last_name" value="Lennon" id="id_last_name" /></p>
<p><label for="id_birthday">Birthday:</label> <input type="text" name="birthday" value="1940-10-9" id="id_birthday" /></p>""")
        self.assertEqual(p.fieldsets[1].as_p(), """<p><label for="id_band">Band:</label> <input type="text" name="band" value="The Beatles" id="id_band" /><input type="hidden" name="secret" value="he didnt say" id="id_secret" /></p>""")

    def test_fieldset_fields_iteration(self):
        # Pass a dictionary to a Form's __init__().
        p = Person(self.some_data)
        for fieldset in p.fieldsets:
            for field in fieldset:
                pass
        self.assertEqual(set([field.name for field in p.fieldsets[0].visible_fields()]), set(['first_name', 'last_name', 'birthday']))
        self.assertEqual(len(p.fieldsets[0].hidden_fields()), 0)
        self.assertEqual(set([field.name for field in p.fieldsets[1].visible_fields()]), set(['band']))
        self.assertEqual(set([field.name for field in p.fieldsets[1].hidden_fields()]), set(['secret']))

    def test_legend_tag(self):
        # Pass a dictionary to a Form's __init__().
        p = Person(self.some_data)
        self.assertIsNone(p.fieldsets[0].legend_tag())
        self.assertEqual(p.fieldsets[1].legend_tag(), """<legend>Additional fields</legend>""")

