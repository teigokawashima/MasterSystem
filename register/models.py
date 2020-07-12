from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin, UserManager, User
from django.core.mail import send_mail
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from project import settings


class Subject(models.Model):
    subject = models.CharField('科目', max_length=30, )

    # kamokuはModelのfield名
    def __str__(self):
        return self.subject


class Video(models.Model):
    title = models.CharField('動画タイトル', max_length=255)
    description = models.TextField('説明(空欄可)', blank=True)
    thumbnail = models.ImageField('サムネイル(空欄可)', upload_to='thumbnails/', null=True, blank=True)
    upload = models.FileField('ファイル', upload_to='uploads/%Y/%m/%d/')  # /media/uploads/2018/3/20/ファイル名
    created_at = models.DateTimeField('作成日', auto_now_add=True)  # default=timezone.nowと違い、入力欄は表示されない
    updated_at = models.DateTimeField('更新日', auto_now=True)  # 更新するたびにその日時が格納される
    subject = models.ForeignKey(
        Subject, verbose_name='科目', on_delete=models.PROTECT
    )
    count = models.IntegerField('再生回数', default=0)
    comment_count = models.IntegerField('コメント数', default=0)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT
    )

    def __str__(self):
        return '{0}{1}{2}'.format(self.title, self.description, self.subject)


class Lecturer(models.Model):
    lecture_name = models.CharField('＜講師＞', max_length=100)
    lecture_email = models.EmailField('講師メール', max_length=100)

    def __str__(self):
        return '{0}{1}'.format(self.lecture_name, self.lecture_email)


class Comment(models.Model):
    title = models.CharField('＜タイトル＞', max_length=255)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, blank=True, null=True
    )
    text = models.TextField('＜コメント＞')
    video = models.ForeignKey(Video, verbose_name='紐づく記事', on_delete=models.CASCADE)
    reply_image1 = models.ImageField('＜画像1を投稿する＞',upload_to='reply_images/', null = True, blank = True)
    reply_image2 = models.ImageField('＜画像2を投稿する＞',upload_to='reply_images/', null = True, blank = True)
    reply_image3 = models.ImageField('＜画像3を投稿する＞',upload_to='reply_images/', null = True, blank = True)
    reply_video = models.FileField('＜動画でコメントする＞', upload_to='reply_videos/%Y/%m/%d/', null = True, blank= True )
    created_at = models.DateTimeField('＜投稿日時＞', default=timezone.now)
    lecturer = models.ForeignKey(
        Lecturer, verbose_name='講師', on_delete=models.PROTECT)


class CustomUserManager(UserManager):
    """ユーザーマネージャー"""
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self._create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """カスタムユーザーモデル

    usernameを使わず、emailアドレスをユーザー名として使うようにしています。

    """
    email = models.EmailField(_('email address'), unique=True)
    first_name = models.CharField(_('first name'), max_length=30, blank=True)
    last_name = models.CharField(_('last name'), max_length=150, blank=True)
    # video = models.ForeignKey(
    #     Video, verbose_name='ビデオ', on_delete=models.PROTECT,blank=True,null=True
    # )

    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_(
            'Designates whether the user can log into this admin site.'),
    )
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)

    objects = CustomUserManager()

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def get_full_name(self):
        """Return the first_name plus the last_name, with a space in
        between."""
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        """Return the short name for the user."""
        return self.first_name

    def email_user(self, subject, message, from_email=None, **kwargs):
        """Send an email to this user."""
        send_mail(subject, message, from_email, [self.email], **kwargs)

    @property
    def username(self):
        return self.email