from django.db import models

class Band(models.Model):
    name = models.CharField(max_length=30)
    band_bottom = models.DecimalField(max_digits = 8, decimal_places=3)
    band_top = models.DecimalField(max_digits = 8, decimal_places=3)

    def __unicode__(self):
        return self.name

class Mode(models.Model):
    name = models.CharField(max_length=30)

    def __unicode__(self):
        return self.name

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

class LogEntry(models.Model):
    contact_log = models.ForeignKey(ContactLog)
    operator = models.ForeignKey(Operator)

    when = models.DateTimeField()
    de_callsign = models.CharField(max_length=10)
    frequency = models.DecimalField(max_digits = 9, decimal_places=4,null=True,blank=True)
    mode = models.ForeignKey(Mode)
    band = models.ForeignKey(Band)
    rst_sent = models.CharField(max_length=3,null=True,blank=True)
    rst_received = models.CharField(max_length=3,null=True,blank=True)

    def __unicode__(self):
        return self.de_callsign

    class Meta:
        verbose_name_plural = "log entries"

    
