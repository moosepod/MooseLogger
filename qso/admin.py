from django.contrib import admin
from qso.models import Ruleset, ContactLog, Operator

admin.site.register(Ruleset)
admin.site.register(ContactLog)
admin.site.register(Operator)

