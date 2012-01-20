from django.contrib import admin
from qso.models import Ruleset, ContactLog, Operator, Mode, Band, Contact,QRZCredentials

import forms

admin.site.register(Band)
admin.site.register(Mode)
admin.site.register(Ruleset)
admin.site.register(ContactLog)
admin.site.register(Operator)
admin.site.register(Contact)

class QRZCredentialsAdmin(admin.ModelAdmin):
	form = forms.QRZCredentialsAdminForm

admin.site.register(QRZCredentials,QRZCredentialsAdmin)
