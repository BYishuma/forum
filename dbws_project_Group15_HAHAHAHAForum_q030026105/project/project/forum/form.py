# coding:utf-8
from django import forms
from forum.models import Post, LoginUser


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('title', 'column', 'content', 'author')


class LoginUserForm(forms.ModelForm):

    username = forms.RegexField(
        max_length=30,
        regex=r'^[\w.@+-]+$',
        error_messages={
            'invalid': "The value can contain only letters, digits, and characters @/./+/-/",
            'required': u"The user name is left blank"
        })
    password = forms.CharField(
        widget=forms.PasswordInput, error_messages={'required': "The password is left blank"})


    class Meta:
        model = LoginUser
        fields = ("username", "email")

    def clean_username(self):
        # Since User.username is unique, this check is redundant,
        # but it sets a nicer error message than the ORM. See #13147.
        username = self.cleaned_data["username"]
        try:
            LoginUser._default_manager.get(username=username)
        except LoginUser.DoesNotExist:
            return username
        raise forms.ValidationError(self.error_messages["duplicate_username"])

    def clean_password_confirm(self):
        password = self.cleaned_data.get("password")
        password_confirm = self.cleaned_data.get("password_confirm")
        if password and password_confirm and password != password_confirm:
            raise forms.ValidationError(
                self.error_messages["password_mismatch"])
        return password_confirm

    def save(self, commit=True):
        user = super(LoginUserForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user
