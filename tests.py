from django.contrib.auth.models import User
from django.test import TestCase

from actiontoken.models import Token, Rule, Field
import app_settings

class ActionTokenTests(TestCase): 
  # simple sanity check tests
  def test_token_create_simple(self):
    token = Token.objects.create(
      user=User.objects.create(username='TEST'),)
    print '\nTest Token Creation'
    print unicode(token)
    self.assertTrue(token)
    self.assertTrue(token.token)
    self.assertTrue(token.expires)

  def test_rule_create(self):
    token = Token.objects.create(
      user=User.objects.create(username='TEST'),)
    rule = Rule.objects.create(
      model='%s.%s' % (User.__module__, User.__name__),
      token=token)
    print '\nTest Rule Creation'
    print unicode(token)
    print unicode(rule)
    self.assertTrue(rule)
    self.assertTrue(rule.is_class())

  def test_field_create(self):
    token = Token.objects.create(
      user=User.objects.create(username='TEST'),)
    rule = Rule.objects.create(
      model='%s.%s' % (User.__module__, User.__name__),
      token=token)
    field = Field.objects.create(
      name='username',
      rule=rule)
    print '\nTest Field Creation'
    print unicode(token)
    print unicode(rule)
    print unicode(field)
    self.assertTrue(field)
    self.assertTrue(field.is_field())

  # TODO: test more complex relationships
