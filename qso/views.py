from django.shortcuts import render_to_response
from django.views.generic import ListView

from qso.models import Ruleset, ContactLog, Operator

class HomeView(ListView):
    context_object_name = "logs"
    template_name = "home.html"

    def get_queryset(self):
        return ContactLog.objects.all().order_by('name')


