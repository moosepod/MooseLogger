from django.db import models
from django.core.exceptions import ValidationError

class BandManager(models.Manager):
    def get_band_for_frequency(self, freq):
        try:
           band = Band.objects.filter(band_bottom__lte=freq, band_top__gte=freq)[0]
        except IndexError:
           band = None

        return band

class Band(models.Model):
    objects = BandManager()

    name = models.CharField(max_length=30,unique=True)
    band_bottom = models.DecimalField(max_digits = 8, decimal_places=3)
    band_top = models.DecimalField(max_digits = 8, decimal_places=3)

    def clean(self):
        if self.band_bottom > self.band_top:
            raise ValidationError('Band bottom must be lower than band top.')

    def save(self, *args, **kwargs):
        self.full_clean()
        
        super(Band,self).save(*args,**kwargs)

    def __unicode__(self):
        return self.name

class Mode(models.Model):
    name = models.CharField(max_length=30,unique=True)

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

class Contact(models.Model):
    contact_log = models.ForeignKey(ContactLog)
    operator = models.ForeignKey(Operator)

    when = models.DateTimeField()
    callsign = models.CharField(max_length=10)
    frequency = models.DecimalField(max_digits = 9, decimal_places=4,null=True,blank=True)
    mode = models.ForeignKey(Mode)
    band = models.ForeignKey(Band)
    rst_sent = models.CharField(max_length=3,null=True,blank=True)
    rst_received = models.CharField(max_length=3,null=True,blank=True)
    contest_exchange_sent = models.CharField(max_length=100, null=True,blank=True)
    contest_exchange_received = models.CharField(max_length=100, null=True,blank=True)

    def __unicode__(self):
        return u'%s, %s' % (self.when, self.callsign)

    
