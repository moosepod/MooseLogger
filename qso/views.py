from django.shortcuts import render_to_response
from django.views.generic import ListView, DetailView, View
from django.shortcuts import get_object_or_404
from django.template import RequestContext

from qso.models import Ruleset, ContactLog, Operator, Contact,QRZCredentials

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
    
    def get_operator(self):
        return Operator.objects.get(callsign='KC2ZUF')  
   
    def get_qrz_info(self):
	try:
	    info = QRZCredentials.objects.filter(operator=self.get_operator)[0]
	    return (info.username, info.password)
	except IndexError:
	    pass
  
        return None

    def get_context_data(self, **kwargs):
        context = {}

        cl = get_object_or_404(ContactLog, pk=kwargs['pk'])
        context['contact_log'] = cl
        context['contacts'] = Contact.objects.filter(contact_log=cl).order_by('-when')

        return context 

    def dispatch(self, request, *args, **kwargs):
        ctx = self.get_context_data(**kwargs)
        form = None

	if not request.session.get('qrz_info'):
	    request.session['qrz_info'] = self.get_qrz_info()

        if request.POST:
            form = ContactForm(data=request.POST)

            if form.is_valid():
                form.save(contact_log=ctx['contact_log'],
                          operator=self.get_operator())
        else:
            form = ContactForm()

        ctx['form'] = form

        return render_to_response('contact_log.html', 
                                 ctx,
                                 RequestContext(request))
       

