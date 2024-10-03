from django import forms
from .models import Members,Hostels
import re
class registration_forms(forms.ModelForm):
    master_key=forms.CharField(max_length=255)
    class Meta:
        model=Members
        fields='__all__'

    def clean(self):
        self.cleaned_data = super().clean()
        first_name=self.cleaned_data.get('first_name','')
        last_name=self.cleaned_data.get('last_name','')
        username=self.cleaned_data.get('username','')
        password=self.cleaned_data.get('password','')
        gender=self.cleaned_data.get('gender','')
        age=self.cleaned_data.get('age','')
        master_key=self.cleaned_data.get('master_key')

        if first_name and not re.match('^[a-zA-Z0-9]{2,255}$',first_name):
            self.add_error('first_name','first name must be letters and digits only.')
        if last_name and not re.match('^[a-zA-Z0-9]{2,255}$',last_name):
            self.add_error('last_name','last name must be letters and digits only.')
        if username and not re.match('^[a-z][a-z0-9.]{2,255}$',username):
            self.add_error('username','username must be letter or digits and . allowed. It should start by letter only.')
        elif Members.objects.filter(username=username):
            self.add_error('username','username already exists, please use another username.')
        if password and not re.match('^[a-zA-Z0-9$@!]{2,15}$',password):
            self.add_error('password','only letters, digits and few special character are allowed.')
        if master_key and master_key != '12345678':
            self.add_error('master_key','Please enter valid master key.')
        
        return self.cleaned_data

class hostel_details_form(forms.ModelForm):
    class Meta:
        model=Hostels
        fields='__all__'
    
    def clean(self):
        self.cleaned_data=super().clean()

        return self.cleaned_data