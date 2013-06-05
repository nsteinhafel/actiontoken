from django.contrib.auth.models import User
from django.test import TestCase

from actiontoken.models import Token, Rule, Field
import app_settings

class ActionTokenTests(TestCase): 
  # simple sanity check tests
  def test_rule_create(self):
    rule = Rule.objects.create(
      action=Rule.CREATE,
      model='%s.%s' % (User.__module__, User.__name__))
    self.assertTrue(rule)
    self.assertTrue(rule.is_class())

  def test_field_create(self):
    rule = Rule.objects.create(
      action=Rule.UPDATE,
      model='%s.%s' % (User.__module__, User.__name__))
    field = Field.objects.create(
      name='username',
      rule=rule)
    self.assertTrue(field)
    self.assertTrue(field.is_field())
    self.assertTrue(field.is_valid_for_rule())

  def test_token_create_simple(self):
    token = Token.objects.create(
      user=User.objects.create(username='TEST'),
      rule=Rule.objects.create(model='%s.%s' % (User.__module__, User.__name__)))
    self.assertTrue(token)
    self.assertTrue(token.token)
    self.assertTrue(token.expires)

  # TODO: test more complex relationships
