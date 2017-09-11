from django import forms
import datetime

class NameForm(forms.Form):
    from_city = forms.CharField(label='from', max_length=100)
    ##to_city =
    Text = forms.CharField(label='Departure date', max_length=20, widget=forms.TextInput(attrs={'id':'datepicker1', 'name':'Text', 'type':'text', 'value':'mm/dd/yyyy', 'onfocus':'this.value = \'\';', 'onblur':'if (this.value == \'\') {this.value = \"mm/dd/yyyy\";}', 'required':''}))
    #id="datepicker1" name="Text" type="text" value="mm/dd/yyyy" onfocus="this.value = '';" onblur="if (this.value == '') {this.value = 'mm/dd/yyyy';}" required="" class="hasDatepicker"
