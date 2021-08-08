from django import forms
from django.contrib.auth.models import User
from django.core.validators import MinLengthValidator, RegexValidator


class UserForm(forms.ModelForm):
    password = forms.CharField(
        label='Password:',
        max_length=100,
        widget=forms.PasswordInput(),
        validators=[
            MinLengthValidator(limit_value=8, message='password should be at least 8 character'),
            RegexValidator(regex="^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]*$",
                           message='password should contain at least one letter and one number')
        ]
    )

    class Meta:
        fields = ['username', 'first_name', 'last_name', 'email']
        model = User

    def save(self, commit=True):
        user = super(UserForm, self).save(commit=False)
        user.set_password(self.cleaned_data.get('password'))
        if commit:
            user.save()
        return user
