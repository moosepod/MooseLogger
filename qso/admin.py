from django.contrib import admin
from qso.models import Ruleset, ContactLog, Operator, Mode, Band, LogEntry

admin.site.register(Band)
admin.site.register(Mode)
admin.site.register(Ruleset)
admin.site.register(ContactLog)
admin.site.register(Operator)
admin.site.register(LogEntry)

