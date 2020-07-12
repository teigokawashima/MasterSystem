from django.conf import settings
from django.contrib.auth import get_user_model, login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import (
    LoginView, LogoutView, PasswordChangeView, PasswordChangeDoneView,
    PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
)
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.core.signing import BadSignature, SignatureExpired, loads, dumps
from django.http import HttpResponseBadRequest
from django.shortcuts import redirect, resolve_url, render
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.views import generic
from .forms import (
    LoginForm, UserCreateForm, UserUpdateForm, MyPasswordChangeForm,
    MyPasswordResetForm, MySetPasswordForm, EmailChangeForm,
    VideoCreateForm, SearchForm, CommentCreateForm
)
from .models import Video, Subject, Comment
from django.shortcuts import get_object_or_404
from django.db.models import Q


User = get_user_model()


class Login(LoginView):
    """ログインページ"""
    form_class = LoginForm
    template_name = 'register/login.html'


class Logout(LogoutView):
    """ログアウトページ"""
    template_name = 'register/top.html'


class UserCreate(generic.CreateView):
    """ユーザー仮登録"""
    template_name = 'register/user_create.html'
    form_class = UserCreateForm

    def form_valid(self, form):
        """仮登録と本登録用メールの発行."""
        # 仮登録と本登録の切り替えは、is_active属性を使うと簡単です。
        # 退会処理も、is_activeをFalseにするだけにしておくと捗ります。
        user = form.save(commit=False)
        user.is_active = False
        user.save()

        # アクティベーションURLの送付
        current_site = get_current_site(self.request)
        domain = current_site.domain
        context = {
            'protocol': 'https' if self.request.is_secure() else 'http',
            'domain': domain,
            'token': dumps(user.pk),
            'user': user,
        }

        subject = render_to_string('register/mail_template/create/subject.txt', context)
        message = render_to_string('register/mail_template/create/message.txt', context)

        user.email_user(subject, message)
        return redirect('register:user_create_done')


class UserCreateDone(generic.TemplateView):
    """ユーザー仮登録したよ"""
    template_name = 'register/user_create_done.html'


class UserCreateComplete(generic.TemplateView):
    """メール内URLアクセス後のユーザー本登録"""
    template_name = 'register/user_create_complete.html'
    timeout_seconds = getattr(settings, 'ACTIVATION_TIMEOUT_SECONDS', 60 * 60 * 24)  # デフォルトでは1日以内

    def get(self, request, **kwargs):
        """tokenが正しければ本登録."""
        token = kwargs.get('token')
        try:
            user_pk = loads(token, max_age=self.timeout_seconds)

        # 期限切れ
        except SignatureExpired:
            return HttpResponseBadRequest()

        # tokenが間違っている
        except BadSignature:
            return HttpResponseBadRequest()

        # tokenは問題なし
        else:
            try:
                user = User.objects.get(pk=user_pk)
            except User.DoesNotExist:
                return HttpResponseBadRequest()
            else:
                if not user.is_active:
                    # まだ仮登録で、他に問題なければ本登録とする
                    user.is_active = True
                    user.save()
                    return super().get(request, **kwargs)

        return HttpResponseBadRequest()


class OnlyYouMixin(UserPassesTestMixin):
    """本人か、スーパーユーザーだけユーザーページアクセスを許可する"""
    raise_exception = True

    def test_func(self):
        user = self.request.user
        return user.pk == self.kwargs['pk'] or user.is_superuser


class UserDetail(OnlyYouMixin, generic.DetailView):
    """ユーザーの詳細ページ"""
    model = User
    template_name = 'register/user_detail.html'  # デフォルトユーザーを使う場合に備え、きちんとtemplate名を書く


class UserUpdate(OnlyYouMixin, generic.UpdateView):
    """ユーザー情報更新ページ"""
    model = User
    form_class = UserUpdateForm
    template_name = 'register/user_form.html'  # デフォルトユーザーを使う場合に備え、きちんとtemplate名を書く

    def get_success_url(self):
        return resolve_url('register:user_detail', pk=self.kwargs['pk'])


class PasswordChange(PasswordChangeView):
    """パスワード変更ビュー"""
    form_class = MyPasswordChangeForm
    success_url = reverse_lazy('register:password_change_done')
    template_name = 'register/password_change.html'


class PasswordChangeDone(PasswordChangeDoneView):
    """パスワード変更しました"""
    template_name = 'register/password_change_done.html'


class PasswordReset(PasswordResetView):
    """パスワード変更用URLの送付ページ"""
    subject_template_name = 'register/mail_template/password_reset/subject.txt'
    email_template_name = 'register/mail_template/password_reset/message.txt'
    template_name = 'register/password_reset_form.html'
    form_class = MyPasswordResetForm
    success_url = reverse_lazy('register:password_reset_done')


class PasswordResetDone(PasswordResetDoneView):
    """パスワード変更用URLを送りましたページ"""
    template_name = 'register/password_reset_done.html'


class PasswordResetConfirm(PasswordResetConfirmView):
    """新パスワード入力ページ"""
    form_class = MySetPasswordForm
    success_url = reverse_lazy('register:password_reset_complete')
    template_name = 'register/password_reset_confirm.html'


class PasswordResetComplete(PasswordResetCompleteView):
    """新パスワード設定しましたページ"""
    template_name = 'register/password_reset_complete.html'


class EmailChange(LoginRequiredMixin, generic.FormView):
    """メールアドレスの変更"""
    template_name = 'register/email_change_form.html'
    form_class = EmailChangeForm

    def form_valid(self, form):
        user = self.request.user
        new_email = form.cleaned_data['email']

        # URLの送付
        current_site = get_current_site(self.request)
        domain = current_site.domain
        context = {
            'protocol': 'https' if self.request.is_secure() else 'http',
            'domain': domain,
            'token': dumps(new_email),
            'user': user,
        }

        subject = render_to_string('register/mail_template/email_change/subject.txt', context)
        message = render_to_string('register/mail_template/email_change/message.txt', context)
        send_mail(subject, message, None, [new_email])

        return redirect('register:email_change_done')


class EmailChangeDone(LoginRequiredMixin, generic.TemplateView):
    """メールアドレスの変更メールを送ったよ"""
    template_name = 'register/email_change_done.html'


class EmailChangeComplete(LoginRequiredMixin, generic.TemplateView):
    """リンクを踏んだ後に呼ばれるメアド変更ビュー"""
    template_name = 'register/email_change_complete.html'
    timeout_seconds = getattr(settings, 'ACTIVATION_TIMEOUT_SECONDS', 60 * 60 * 24)  # デフォルトでは1日以内

    def get(self, request, **kwargs):
        token = kwargs.get('token')
        try:
            new_email = loads(token, max_age=self.timeout_seconds)

        # 期限切れ
        except SignatureExpired:
            return HttpResponseBadRequest()

        # tokenが間違っている
        except BadSignature:
            return HttpResponseBadRequest()

        # tokenは問題なし
        else:
            User.objects.filter(email=new_email, is_active=False).delete()
            request.user.email = new_email
            request.user.save()
            return super().get(request, **kwargs)


@login_required
def videolistfunc(request):
    # user はVideoモデルが保有する変数userのこと、このuserが現在ログインしているユーザー（request.user）と一致するかどうかを下の行で調べている。
    object_list = Video.objects.order_by('-created_at').filter(user=request.user)
    return render(request, 'register/video_list.html', {'object_list': object_list})


class IndexView(generic.ListView):
    model = Video
    template_name = "register/video_list.html"

    def get_context_data(self):
        # queryset = Video.objects.filter(user=self.request.user)
        context = super().get_context_data()
        context['form'] = SearchForm(self.request.GET)
        # ['forms']じゃなくて['form']気をつけろ！
        return context

    def get_queryset(self):
        form = SearchForm(self.request.GET)
        form.is_valid()

        # queryset = super().get_queryset()
        queryset = Video.objects.order_by('-created_at').filter(user=self.request.user)

        subject = form.cleaned_data['subject']
        if subject:
            queryset = queryset.filter(subject=subject)
        return queryset

    def get_queryset(self):
        queryset = Video.objects.order_by('-created_at').filter(user=self.request.user)
        keyword = self.request.GET.get('keyword')
        if keyword:
            queryset = queryset.filter(
                Q(description__icontains=keyword) | Q(title__icontains=keyword))
        return queryset


class SubjectView(generic.ListView):
    model = Video

    def get_queryset(self):
        subject = get_object_or_404(Subject, pk=self.kwargs['pk'])
        queryset = Video.objects.order_by('-created_at').filter(user=self.request.user).filter(subject=subject)
        return queryset


class CreateView(generic.CreateView):
    model = Video
    form_class = VideoCreateForm

    def form_valid(self, form):
        video = form.save(commit=False)
        video.save()
        user_email = video.user.email
        title = form.cleaned_data['title']
        description = form.cleaned_data['description']
        # from_email = None

        current_site = get_current_site(self.request)
        domain = current_site.domain
        context = {
            'protocol': 'https' if self.request.is_secure() else 'http',
            'domain': domain,
            'video': video,
        }

        subject = render_to_string('register/mail_template/video_upload_reminder_messages/subject')
        message = render_to_string('register/mail_template/video_upload_reminder_messages/message', context)

        send_mail(subject, message, None, [user_email])
        return redirect('register:index')

    # success_url = reverse_lazy('register:index')


class PlayView(generic.DetailView):
    model = Video

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        obj.count += 1

        obj.save()
        return obj


class CommentView(generic.CreateView):
    model = Comment
    form_class = CommentCreateForm

    def form_valid(self, form):
        video_pk = self.kwargs['video_pk']
        comment = form.save(commit=False)
        comment.video = get_object_or_404(Video, pk=video_pk)
        comment.save()
        commenter_email = comment.video.user.email

        comment.video.comment_count += 1
        comment.video.save()
        if comment.lecturer.lecture_email:
            lecturer_email = comment.lecturer.lecture_email
        else:
            lecturer_email = 'circlebeam1906@gmail.com'

        seigakusha_email = 'circlebeam1906@gmail.com'
        current_site = get_current_site(self.request)
        domain = current_site.domain
        context = {
            'protocol': 'https' if self.request.is_secure() else 'http',
            'domain': domain,
            'token': video_pk,
            'comment': comment,
            'lecturer_email': lecturer_email
        }

        subject = render_to_string('register/mail_template/comment_message/subject.txt', context)
        message = render_to_string('register/mail_template/comment_message/message.txt', context)
        send_mail(subject, message, None, [commenter_email, lecturer_email, seigakusha_email])
        return redirect('register:play', pk=video_pk)


class DeleteView(generic.DeleteView):
    model = Video
    success_url = reverse_lazy('register:index')


class CommentDeleteView(generic.DeleteView):
    model = Comment
    template_name = "register/comment_confirm_delete.html"

    def get_success_url(self):
        obj = super().get_object(queryset=None)
        obj.save()
        obj.video.comment_count -= 1
        obj.video.save()
        pk = obj.video.pk
        return reverse_lazy("register:play", kwargs={'pk':pk})


class AllVideosView(generic.ListView):
    model = Video
    context_object_name = 'all_video_list'
    template_name = "register/all_video_list.html"

    def get_queryset(self):
        queryset = Video.objects.order_by('-created_at')
        master_keyword = self.request.GET.get('master_keyword')
        # self.GET.get('master_keyword')は辞書型のデータ。　keywordで入力された文字列がkeyになり、インスタンスがデータになる。
        # {'keyword': 'インスタンス'}といった感じ。
        if master_keyword:
            queryset = queryset.filter(
                Q(description__icontains=master_keyword) | Q(title__icontains=master_keyword)
                # | Q(user__icontains=master_keyword) userは文字列ではなくユーザーインスタンスだからキーワード検索できない。
                | Q(user__email__icontains=master_keyword)
            )
        """ 
        Q(user__email__icontains=master_keyword)について
        userはForeignkeyなのでUserクラスの属性であるemailにアクセスさせるためには
        user__emailとする必要がある。この時ハイフン（__）が2つ必要であることに注意。
        なぜなら、属性名の中に、ハイフン(_)を含むものと区別できなくなってしまうため。
        """
        return queryset