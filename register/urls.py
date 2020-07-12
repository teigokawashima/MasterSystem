from django.urls import path
from . import views
from .views import videolistfunc

app_name = 'register'

urlpatterns = [
    # path('', views.Top.as_view(), name='top'),
    path('', views.Login.as_view(), name='login'),
    # path('login/',loginfunc,name='login'),
    path('logout/', views.Logout.as_view(), name='logout'),
    path('user_create/', views.UserCreate.as_view(), name='user_create'),
    path('user_create/done/', views.UserCreateDone.as_view(), name='user_create_done'),
    path('user_create/complete/<token>/', views.UserCreateComplete.as_view(), name='user_create_complete'),
    path('user_detail/<int:pk>/', views.UserDetail.as_view(), name='user_detail'),
    path('user_update/<int:pk>/', views.UserUpdate.as_view(), name='user_update'),
    path('password_change/', views.PasswordChange.as_view(), name='password_change'),
    path('password_change/done/', views.PasswordChangeDone.as_view(), name='password_change_done'),
    path('password_reset/', views.PasswordReset.as_view(), name='password_reset'),
    path('password_reset/done/', views.PasswordResetDone.as_view(), name='password_reset_done'),
    path('password_reset/confirm/<uidb64>/<token>/', views.PasswordResetConfirm.as_view(),
         name='password_reset_confirm'),
    path('password_reset/complete/', views.PasswordResetComplete.as_view(), name='password_reset_complete'),
    path('email/change/', views.EmailChange.as_view(), name='email_change'),
    path('email/change/done/', views.EmailChangeDone.as_view(), name='email_change_done'),
    path('email/change/complete/<str:token>/', views.EmailChangeComplete.as_view(), name='email_change_complete'),

    path('list/', videolistfunc, name='index'),
    path('index/', views.IndexView.as_view(), name='second_index'),

    path('upload/', views.CreateView.as_view(), name='upload'),
    path('play/<int:pk>/', views.PlayView.as_view(), name='play'),
    path('subject/<int:pk>/', views.SubjectView.as_view(), name='subject'),

    path('delete/<int:pk>/', views.DeleteView.as_view(), name='delete'),
    path('comment/<int:video_pk>/',views.CommentView.as_view(), name='comment'),
    path('allvideolist/', views.AllVideosView.as_view(), name='all_videos'),
    path('commentdelete/<int:pk>/', views.CommentDeleteView.as_view(), name='comment_delete'),

]