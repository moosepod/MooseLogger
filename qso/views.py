from django.shortcuts import render_to_response
from django.views.generic import ListView, DetailView

from qso.models import Ruleset, ContactLog, Operator, LogEntry

class HomeView(ListView):
    context_object_name = "logs"
    template_name = "home.html"

    def get_queryset(self):
        return ContactLog.objects.all().order_by('name')


class ContactLogView(DetailView):
    template_name = "contact_log.html"
    context_object_name = "contact_log"

    queryset = ContactLog.objects.all()

    def get_context_data(self, **kwargs):
        context = super(ContactLogView, self).get_context_data(**kwargs)

        context['log_entries'] = LogEntry.objects.filter(contact_log=self.get_object()
                                                         ).order_by('-when')

        
        return context

