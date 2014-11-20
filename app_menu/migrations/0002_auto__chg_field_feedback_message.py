# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'Feedback.message'
        db.alter_column(u'app_menu_feedback', 'message', self.gf('django.db.models.fields.TextField')(max_length=50000))

    def backwards(self, orm):

        # Changing field 'Feedback.message'
        db.alter_column(u'app_menu_feedback', 'message', self.gf('djangocms_text_ckeditor.fields.HTMLField')(max_length=50000))

    models = {
        u'app_menu.feedback': {
            'Meta': {'object_name': 'Feedback'},
            'date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2014, 11, 20, 0, 0)'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '100', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'message': ('django.db.models.fields.TextField', [], {'default': 'None', 'max_length': '50000'}),
            'subject': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'username': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'})
        }
    }

    complete_apps = ['app_menu']