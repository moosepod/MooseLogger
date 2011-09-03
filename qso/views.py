from django.shortcuts import render_to_response
from django.views.generic import ListView, DetailView, View
from django.shortcuts import get_object_or_404
from django.template import RequestContext

from qso.models import Ruleset, ContactLog, Operator, Contact

from qso.forms import ContactForm

class HomeView(ListView):
    context_object_name = "logs"
    template_name = "home.html"

    def get_queryset(self):
        return ContactLog.objects.all().order_by('name')


class ContactLogView(View):
    template_name = "contact_log.html"
    context_object_name = "contact_log"
    form_class = ContactForm

    queryset = ContactLog.objects.all()

    def get_context_data(self, **kwargs):
        context = {}

        cl = get_object_or_404(ContactLog, pk=kwargs['pk'])
        context['contact_log'] = cl
        context['contacts'] = Contact.objects.filter(contact_log=cl).order_by('-when')

        return context 

    def dispatch(self, request, *args, **kwargs):
        ctx = self.get_context_data(**kwargs)
        form = None

        if request.POST:
            form = ContactForm(data=request.POST)
            if form.is_valid():
                form.save()
        else:
            form = ContactForm()

        ctx['form'] = form

        return render_to_response('contact_log.html', 
                                 ctx,
                                 RequestContext(request))
       

