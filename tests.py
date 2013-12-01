from datetime import datetime

from django.contrib.auth.models import User
from django.test import TestCase

from actiontoken.exceptions import InvalidModelName, InvalidActionTarget
from actiontoken.models import Token, Rule, Field, Action

import app_settings

class ActionTokenTests(TestCase): 
  def test_token_simple(self):
    token = Token.objects.create()
    self.assertTrue(token)
    self.assertTrue(token.token)
    self.assertTrue(token.expires)

    token = Token.objects.create(
      user=User.objects.create(username='TEST'),
      token='asdf',
      expires=datetime.now(),)
    self.assertTrue(token)
    self.assertTrue(token.token)
    self.assertTrue(token.expires)

  def test_rule_simple(self):
    token = Token.objects.create()
    rule = Rule.objects.create(
      model='%s.%s' % (User.__module__, User.__name__),
      token=token)
    self.assertTrue(rule)
    self.assertTrue(rule.is_class())

  def test_field_simple(self):
    token = Token.objects.create()
    rule = Rule.objects.create(
      model='%s.%s' % (User.__module__, User.__name__),
      token=token)
    field = Field.objects.create(
      name='username',
      rule=rule)
    self.assertTrue(field)
    self.assertTrue(field.is_field())

  # let's throw in Actions

  def test_rule_action_simple(self):
    token = Token.objects.create(
      user=User.objects.create(username='TEST'),)
    rule = Rule.objects.create(
      model='%s.%s' % (User.__module__, User.__name__),
      token=token)
    action = Action.objects.create(
      rule=rule)

    self.assertTrue(action.has_valid_action())
    self.assertTrue(action.has_valid_target())
    self.assertTrue(token.can_read(User))

  def test_field_action_simple(self):
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

    self.assertTrue(action.has_valid_action())
    self.assertTrue(action.has_valid_target())
    self.assertTrue(token.can_read(User, 'username'))

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

    try:
      action.save()
      self.fail()
    except InvalidActionTarget: pass
      
    action.rule = None
    self.assertTrue(action.has_valid_target())

  def test_rule_action_create_simple(self):
    token = Token.objects.create()
    rule = Rule.objects.create(
      model='%s.%s' % (User.__module__, User.__name__),
      token=token)
    action = Action.objects.create(
      action=Action.CREATE,
      rule=rule)
    self.assertTrue(token.can_create(User))

  # haven't decided how I want the string representations to look, so keeping it simple

  def test_unicode_simple(self):
    token = Token.objects.create()
    rule = Rule.objects.create(
      model='%s.%s' % (User.__module__, User.__name__),
      token=token)
    field = Field.objects.create(
      name='username',
      rule=rule)
    action = Action.objects.create(
      field=field)

    self.assertTrue(len(unicode(token))   > 0)
    self.assertTrue(len(unicode(rule))    > 0)
    self.assertTrue(len(unicode(field))   > 0)
    self.assertTrue(len(unicode(action))  > 0)

    print '\nunicode test'
    print unicode(token)
    print unicode(rule)
    print unicode(field)
    print unicode(action)

  # TODO: test more complex relationships
