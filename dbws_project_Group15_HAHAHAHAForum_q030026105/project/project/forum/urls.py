import notifications
from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.urls import path, re_path, include

from . import views
from .views import IndexView, UserPostView

admin.autodiscover()

urlpatterns = [
    # path(r'', views.index),
    re_path(r'login', views.userlogin, name='user_login'),  ####page-login.html                {%url 'user_login'%}
    re_path(r'logout', views.userlogout, name='user_logout'),
    re_path(r'register', views.userregister, name='user_register'),
    re_path(r'column(?P<column_pk>\d+)', views.columndetail, name='single_category'),##page-signup.html        {%url 'user_register'%}
    re_path(r'post(?P<post_pk>\d+)', views.singletopic, name='single_topic'),
    ##page-single-topic.html  {%url 'single_topic'%}
    ############### re_path(r'post_create', login_required(PostCreate.as_view()), name='post_create'),
    ###############re_path(r'^column/(?P<column_pk>\d+)/$', views.columndetail,name='column_detail'),

    ##page-categories-single.html  {%url 'single_category'%}
    re_path(r'categories', views.columnall, name='categories'),  ##page-categories.html    {%url 'categories'%}

    re_path(r'visual', views.visualized, name='visual'),
    # re_path(r'singletopic', views.singletopic, name='single_topic'),
    # re_path(r'postdetail',views.pos)
    re_path(r'makecomment', views.makecomment, name='make_comment'),
    re_path(r'userpage', UserPostView.as_view(), name='user_page'),
    re_path(r'post_create', views.PostCreate, name='post_create'),
    re_path(r'search', views.search, name='search'),
    # re_path(r'post_create', PostCreate.as_view(), name='post_create'),
    ##page-create-topic.html      {%url 'post_create'%}
    re_path(r'notification/', include('notifications.urls', namespace='notifications')),

    # re_path(r'column', views.columndetail, name='single_category'),
    re_path(r'', IndexView.as_view(), name='index'),  ##index.html   {%url 'index'%}

    # re_path(r'^columns/$', views.columnall, name='column_all'),
]
