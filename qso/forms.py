import datetime

from django import forms

from qso.models import Contact,Mode,Band

VALID_RST_RE = '^[1-5][1-9N][1-9N]?$'

class ContactForm(forms.Form):
    when = forms.DateTimeField(required=False)
    callsign = forms.CharField(max_length=10,
                               widget=forms.TextInput(attrs={'size':'10'}),
                               error_messages={'required': 'Please provide the contact\'s callsign.'})
    frequency = forms.CharField(required=False,
                               widget=forms.TextInput(attrs={'size':'10'}))
    mode = forms.ModelChoiceField(queryset=Mode.objects.all(),
                                  error_messages={'required': 'Please select a mode.'})
    band = forms.ModelChoiceField(queryset=Band.objects.all(),required=False)
    rst_sent = forms.RegexField(required=False,
                                regex=VALID_RST_RE,
                                widget=forms.TextInput(attrs={'size':'3'}),
                                error_messages={'invalid': 'RST Sent should be in the format 59 or 599.'})
    rst_received = forms.RegexField(required=False,
                                regex=VALID_RST_RE,
                                widget=forms.TextInput(attrs={'size':'3'}),
                                error_messages={'invalid': 'RST Received should be in the format 59 or 599.'})
    contest_exchange_sent = forms.CharField(required=False,
                                widget=forms.TextInput(attrs={'size':'10'}))
    contest_exchange_received = forms.CharField(required=False,
                                widget=forms.TextInput(attrs={'size':'10'}))

    def clean_frequency(self):
        freq = self.cleaned_data.get('frequency')

        if freq:
            try:
                float(freq)
            except ValueError:
                raise forms.ValidationError('Please enter frequency in the format 7.123')

        return freq

    def clean_when(self):
        when = self.cleaned_data.get('when')

        if not when:
            when = datetime.datetime.utcnow()

        return when

    def clean(self):
        if not self.cleaned_data.get('band'):
          freq = self.cleaned_data.get('frequency')

          if not freq:
            band = None
          else:
            band = Band.objects.get_band_for_frequency(freq)
            
          if not band:
            raise forms.ValidationError('Please select a band or enter a frequency.')
          else:
            self.cleaned_data['band'] = band

        return self.cleaned_data

    def save(self, contact_log, operator):

        contact = Contact(contact_log=contact_log,
                                         operator=operator,
                                         callsign=self.cleaned_data['callsign'],
                                         band=self.cleaned_data['band'],
                                         mode=self.cleaned_data['mode'],
                                         when=self.cleaned_data['when'],
                                         rst_sent=self.cleaned_data['rst_sent'],
                                         rst_received=self.cleaned_data.get('rst_received'),
                                         contest_exchange_sent=self.cleaned_data.get('contest_exchange_sent'),
                                         contest_exchange_received=self.cleaned_data.get('contest_exchange_received'))

        if self.cleaned_data.get('frequency'):
            contact.frequency = self.cleaned_data.get('frequency')

        contact.save()

        return contact    

