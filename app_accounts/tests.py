from django.test import TestCase, RequestFactory
from django.test.client import Client
from django.contrib.auth.models import AnonymousUser, User
from django.core.urlresolvers import reverse, resolve
import json

class TestAjaxCheckUsername(TestCase):
	def setUp(self):
		self.client = Client()
		self.record = User.objects.create(
			id=22, 
			username='qqqqqq', 
			password='pbkdf2_sha256$12000$Bm1GmmeGtnyU$v4E1UUcXWjk7pmQEkIWXvY2Hsw2ycG783R/bVpoVEWk=', 
			is_active=1, 
			is_staff=0,
			is_superuser=0,
			email='asasas@mail.ru'
		)

	def test_diary(self):  
		json_string = json.dumps({'username':'qqqqqq'})  

		self.response = self.client.post('/ajax_username_check/', json_string, "text/json", HTTP_X_REQUESTED_WITH='XMLHttpRequest')
		self.assertContains(self.response, 'true')									

