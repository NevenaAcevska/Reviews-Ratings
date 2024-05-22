from django import forms
from Reviewa.models import User, Feedback

from django import forms

class CustomRatingWidget(forms.Widget):
    template_name = 'custom_rating_widget.html'

    def get_context(self, name, value, attrs=None):
        return {'widget': {
            'name': name,
            'value': value,
            'attrs': self.build_attrs(attrs),
            'choices': ['1', '1.5', '2', '2.5', '3', '3.5', '4', '4.5', '5'],
        }}

    def value_from_datadict(self, data, files, name):
        return data.get(name)

class CustomRatingField(forms.Field):
    widget = CustomRatingWidget
    default_error_messages = {
        'invalid': 'Enter a valid rating.',
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def to_python(self, value):
        if value in self.empty_values:
            return None
        try:
            return float(value)
        except (TypeError, ValueError):
            raise forms.ValidationError(self.error_messages['invalid'], code='invalid')

    def validate(self, value):
        super().validate(value)
        if value not in [1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0]:
            raise forms.ValidationError(self.error_messages['invalid'], code='invalid')




class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'phone']


class FeedbackForm(forms.ModelForm):
    rate = CustomRatingField(label='Rate')

    class Meta:
        model = Feedback
        fields = ['product', 'rate', 'comment']
