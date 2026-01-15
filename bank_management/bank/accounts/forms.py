from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from .models import Profile
from branches.models import Branch
# register form
class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())
    branch = forms.ModelChoiceField(
        queryset=Branch.objects.all(),
        empty_label="Select Branch",
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password']  # only User fields here

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])

        if commit:
            user.save()  # triggers signal → Profile & Account created

            # Update Profile with branch
            profile = Profile.objects.get(user=user)
            profile.branch = self.cleaned_data['branch']
            profile.role = 'customer'  # default role
            profile.save()

        return user
# login form
class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput()) # username data
    password = forms.CharField(widget=forms.PasswordInput()) # password data
# edit profile
# class ProfileEditForm(forms.ModelForm):
#     class Meta:
#         model = Profile
#         fields = ['image', 'first_name', 'last_name', 'email']  # include image field here
#         widgets = {
#             'image': forms.ClearableFileInput(attrs={
#                 'class': 'form-control',
#                 'show_clear': False,  # This option doesn’t actually exist, but you can override render
#             }),
#             'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}),
#             'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}),
#             'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
#         }

class CustomerMessageForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['message']
        widgets = {
            'message': forms.Textarea(attrs={'class':'form-control','rows': 3, 'placeholder': 'Type your message to manager...'})
        }
