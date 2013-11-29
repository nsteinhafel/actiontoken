from django.contrib.auth.models import User
from django.test import TestCase

from actiontoken.models import Token, Rule, Field, Action
import app_settings

class ActionTokenTests(TestCase): 

  # simple sanity check tests

  def test_token_create_simple(self):
    token = Token.objects.create(
      user=User.objects.create(username='TEST'),)
    self.assertTrue(token)
    self.assertTrue(token.token)
    self.assertTrue(token.expires)

    print '\nTest Token Creation'
    print unicode(token)

  def test_rule_create(self):
    token = Token.objects.create(
      user=User.objects.create(username='TEST'),)
    rule = Rule.objects.create(
      model='%s.%s' % (User.__module__, User.__name__),
      token=token)
    self.assertTrue(rule)
    self.assertTrue(rule.is_class())

    print '\nTest Rule Creation'
    print unicode(token)
    print unicode(rule)

  def test_field_create(self):
    token = Token.objects.create(
      user=User.objects.create(username='TEST'),)
    rule = Rule.objects.create(
      model='%s.%s' % (User.__module__, User.__name__),
      token=token)
    field = Field.objects.create(
      name='username',
      rule=rule)
    self.assertTrue(field)
    self.assertTrue(field.is_field())

    print '\nTest Field Creation'
    print unicode(token)
    print unicode(rule)
    print unicode(field)

  # let's throw in Actions

  def test_rule_action_create(self):
    token = Token.objects.create(
      user=User.objects.create(username='TEST'),)
    rule = Rule.objects.create(
      model='%s.%s' % (User.__module__, User.__name__),
      token=token)
    action = Action.objects.create()
    self.assertTrue(action.has_valid_action())
    self.assertFalse(action.has_valid_target())
    action.rule = rule
    action.save()
    self.assertTrue(action.has_valid_target())
    self.assertTrue(token.can_read(User))

    print '\nTest Rule-Action (Read) Creation'
    print unicode(token)
    print unicode(rule)
    print unicode(action)

  def test_field_action_create(self):
    token = Token.objects.create(
      user=User.objects.create(username='TEST'),)
    rule = Rule.objects.create(
      model='%s.%s' % (User.__module__, User.__name__),
      token=token)
    field = Field.objects.create(
      name='username',
      rule=rule)
    action = Action.objects.create()
    self.assertTrue(action.has_valid_action())
    self.assertFalse(action.has_valid_target())
    action.field = field
    action.save()
    self.assertTrue(action.has_valid_target())
    self.assertTrue(token.can_read(User, 'username'))

    print '\nTest Field-Action (Read) Creation'
    print unicode(token)
    print unicode(rule)
    print unicode(field)
    print unicode(action)

  def test_rule_field_conflict_for_action(self):
    token = Token.objects.create(
      user=User.objects.create(username='TEST'),)
    rule = Rule.objects.create(
      model='%s.%s' % (User.__module__, User.__name__),
      token=token)
    field = Field.objects.create(
      name='username',
      rule=rule)
    action = Action.objects.create(
      field=field)
    self.assertTrue(action.has_valid_target())
    action.rule = rule
    self.assertFalse(action.has_valid_target())
    action.rule = None
    self.assertTrue(action.has_valid_target())

    print '\nTest Rule-Field Conflict for Action'
    print unicode(token)
    print unicode(rule)
    print unicode(field)
    print unicode(action)

  # TODO: test more complex relationships
