from django import forms
from django.contrib.auth.forms import (
    AuthenticationForm, UserCreationForm, PasswordChangeForm,
    PasswordResetForm, SetPasswordForm
)
from django.contrib.auth import get_user_model
from .models import Video, Subject, Comment

User = get_user_model()


class EmailChangeForm(forms.ModelForm):
    """メールアドレス変更フォーム"""

    class Meta:
        model = User
        fields = ('email',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

    def clean_email(self):
        email = self.cleaned_data['email']
        User.objects.filter(email=email, is_active=False).delete()
        return email


class LoginForm(AuthenticationForm):
    """ログインフォーム"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['placeholder'] = field.label  # placeholderにフィールドのラベルを入れる


class UserCreateForm(UserCreationForm):
    """ユーザー登録用フォーム"""
    class Meta:
        model = User
        fields = ('email',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

    def clean_email(self):
        email = self.cleaned_data['email']
        User.objects.filter(email=email, is_active=False).delete()
        return email

class UserUpdateForm(forms.ModelForm):
    """ユーザー情報更新フォーム"""

    class Meta:
        model = User
        fields = ('last_name', 'first_name',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'


class MyPasswordChangeForm(PasswordChangeForm):
    """パスワード変更フォーム"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'


class MyPasswordResetForm(PasswordResetForm):
    """パスワード忘れたときのフォーム"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'


class MySetPasswordForm(SetPasswordForm):
    """パスワード再設定用フォーム(パスワード忘れて再設定)"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'


class VideoCreateForm(forms.ModelForm):
    class Meta:
        model = Video
        fields = ('title', 'description', 'thumbnail', 'upload','subject', 'user')

        widgets = {
            'title': forms.TextInput(attrs={  # <input type="text" class="form-control"
                'class': 'form-control',
            }),
            'description': forms.Textarea(attrs={  # <textarea class="form-cotrol"
                'class': 'form-control',
            }),
            'thumbnail': forms.ClearableFileInput(attrs={  # <input type="file" class="form-control-file"
                'class': "form-control-file",
            }),
            'upload': forms.ClearableFileInput(attrs={
                'class': "form-control-file",
            }),
        }


class CommentCreateForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ('title', 'text', 'reply_image1', 'reply_image2', 'reply_image3', 'reply_video', 'lecturer')

        widgets = {
            'title': forms.TextInput(attrs={  # <input type="text" class="form-control"
                'class': 'form-control',
            }),
            'text': forms.Textarea(attrs={  # <textarea class="form-cotrol"
                'class': 'form-control',
            }),
            'reply_image1': forms.ClearableFileInput(attrs={  # <input type="file" class="form-control-file"
                'class': "form-control-file",
            }),
            'reply_image2': forms.ClearableFileInput(attrs={  # <input type="file" class="form-control-file"
                'class': "form-control-file",
            }),
            'reply_image3': forms.ClearableFileInput(attrs={  # <input type="file" class="form-control-file"
                'class': "form-control-file",
            }),
            'reply_video': forms.ClearableFileInput(attrs={
                'class': "form-control-file",
            })
        }


class SearchForm(forms.Form):
    subject = forms.ModelChoiceField(
        queryset=Subject.objects, label='科目', required=False
    )