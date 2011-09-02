from django.db import models

class Operator(models.Model):
    callsign = models.CharField(max_length=10)

    def __unicode__(self):
        return self.callsign

class Ruleset(models.Model):
    name = models.CharField(unique=True, max_length=255)
    created_on = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return self.name

class ContactLog(models.Model):
    name = models.CharField(max_length=255)
    ruleset = models.ForeignKey(Ruleset)
    owner = models.ForeignKey(Operator)
    created_on = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return self.name

