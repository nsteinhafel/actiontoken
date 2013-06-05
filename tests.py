from datetime import datetime
from hashlib import sha1

from django.contrib.auth.models import User
from django.test import TestCase

from actiontoken.models import Token, Rule, Field
import app_settings

class ActionTokenTests(TestCase):
  def setUp(self):
    user_test = User.objects.create(username='TESTUSERNAME')
    rule_readuser = Rule.objects.create(model='django.contrib.auth.models.User')
    Token.objects.create(
      token=sha1('1').hexdigest(),
      expires=datetime.now() + app_settings.DEFAULT_EXPIRATION,
      user=user_test,
      rule=rule_readuser)
    Token.objects.create(
      token=sha1('2').hexdigest(),
      expires=datetime.now() + app_settings.DEFAULT_EXPIRATION,
      user=user_test,
      rule=rule_readuser)
  
  def test_token_create(self):
    self.assertTrue(Token.objects.get(token=sha1('1').hexdigest()))

  #def test_token_valid_rule(self):
