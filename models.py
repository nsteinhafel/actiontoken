from datetime import datetime
from hashlib import sha1
from random import random

from django.contrib.auth.models import User
from django.db import models

import app_settings

class Token(models.Model):
  token = models.CharField(max_length=40)
  expires = models.DateTimeField()
  # user performing action
  user = models.ForeignKey(User)
  
  # use on save if no token assigned
  def __create_token(self):
    self.token = sha1(str(datetime.now()) + str(random())).hexdigest()

  # use on save if no expiration assigned
  def __set_expiration(self):
    self.expires = datetime.now() + app_settings.DEFAULT_EXPIRATION

  def can_create(self, model, field=None):
    return any(r.can_create(model, field) for r in Rule.objects.filter(token=self))

  def can_read(self, model, field=None):
    return any(r.can_read(model, field) for r in Rule.objects.filter(token=self))

  def can_udpate(self, model, field=None):
    return any(r.can_update(model, field) for r in Rule.objects.filter(token=self))

  def can_delete(self, model, field=None):
    return any(r.can_delete(model, field) for r in Rule.objects.filter(token=self))


  def save(self, *args, **kwargs):
    # full_clean?
    if not self.token:
      self.__create_token()
    if not self.expires:
      self.__set_expiration()
    super(Token, self).save(*args, **kwargs)

  def __unicode__(self):
    return 'Token %s for user %s expires on %s' % (self.token, self.user, self.expires)

class InvalidModelName(Exception):
  pass

class Rule(models.Model):
  model = models.TextField()
  token = models.ForeignKey(Token)

  def can_create(self, model, field=None):
    if field:
      return any(f.can_create() for f in Field.objects.filter(rule=self).filter(name=field))
    return self.get_class() == model and any(a.is_create() for a in Action.objects.filter(rule=self))

  def can_read(self, model, field=None):
    if field:
      return any(f.can_read() for f in Field.objects.filter(rule=self).filter(name=field))
    return self.get_class() == model and any(a.is_read() for a in Action.objects.filter(rule=self))

  def can_udpate(self, model, field=None):
    if field:
      return any(f.can_update() for field in Field.objects.filter(rule=self).filter(name=field))
    return self.get_class() == model and any(a.is_update() for a in Action.objects.filter(rule=self))

  def can_delete(self, model, field=None):
    if field:
      return any(f.can_delete() for field in Field.objects.filter(rule=self).filter(name=field))
    return self.get_class() == model and any(a.is_delete() for a in Action.objects.filter(rule=self))

  def is_class(self):
    return isinstance(self.get_class(), type)

  # revisit this later
  def get_class(self):
    import_dict = self.model.rsplit('.', 1)
    if not len(import_dict) == 2:
      raise InvalidModelName('Model could not be imported (is it fully qualified?).')
    return getattr(__import__(import_dict[0], fromlist=[import_dict[1]]), import_dict[1])

  def save(self, *args, **kwargs):
    # full_clean?
    super(Rule, self).save(*args, **kwargs)

  def __unicode__(self):
    return 'Rule for %s (%s)' % (self.model, ', '.join(unicode(a) for a in Action.objects.filter(rule=self)))

class Field(models.Model):
  name = models.TextField()
  rule = models.ForeignKey(Rule)

  def can_create(self):
    return any(a.is_create() for a in Action.objects.filter(field=self))

  def can_read(self):
    return any(a.is_read() for a in Action.objects.filter(field=self))

  def can_udpate(self):
    return any(a.is_update() for a in Action.objects.filter(field=self))

  def can_delete(self):
    return any(a.is_delete() for a in Action.objects.filter(field=self))

  def is_field(self):
    return self.name in map(lambda x: x.name, self.rule.get_class()._meta.fields)

  def save(self, *args, **kwargs):
    # full_clean?
    super(Field, self).save(*args, **kwargs)

  def __unicode__(self):
    return 'Field %s (%s)' % (self.name, ', '.join(unicode(a) for a in Action.objects.filter(field=self)))

class Action(models.Model):
  CREATE  = 'C'
  READ    = 'R'
  UPDATE  = 'U'
  DELETE  = 'D'
  ACTIONS = (
    (CREATE,  'Create'),
    (READ,    'Read'), 
    (UPDATE,  'Update'), 
    (DELETE,  'Delete'),
  )
  
  action = models.CharField(max_length=1, choices=ACTIONS, default=READ)
  rule = models.ForeignKey(Rule, blank=True, null=True)
  field = models.ForeignKey(Field, blank=True, null=True)

  def has_valid_action(self):
    return self.action in [a[0] for a in Action.ACTIONS]

  # there can only be one target and action must have a target
  def has_valid_target(self):
    return (self.rule != None) != (self.field != None)

  def is_create(self):
    return self.action == Action.CREATE

  def is_read(self):
    return self.action == Action.READ

  def is_update(self):
    return self.action == Action.UPDATE

  def is_delete(self):
    return self.action == Action.DELETE

  def save(self, *args, **kwargs):
    # full_clean?
    super(Action, self).save(*args, **kwargs)

  def __unicode__(self):
    return dict(Action.ACTIONS)[self.action]
