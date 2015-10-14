from django.conf.urls import patterns, include, url
from django.contrib import admin
from crpt201510.settings import STATIC_ROOT
from django.contrib import auth
import django.views.i18n

urlpatterns = patterns('',

    # url to form login
    url(r'^accounts/login/$', 'crpt201510.views.my_login', name="my_login"),

    # url to logout page
    url(r'^logout/$', 'crpt201510.views.my_logout', name='logout'),

    # url to change password
    url(r'^accounts/change_password/$', 'crpt201510.views.my_change_password', name='my_change_password'),

    # urls to manage the forgot password link
    url(r'^admin/password_reset/$', 'django.contrib.auth.views.password_reset', name='password_reset'),

    url(r'^password_reset/done/$', 'django.contrib.auth.views.password_reset_done', name='password_reset_done'),
    url(r'^reset/(?P<uidb64>[^/]+)/(?P<token>[^/]+)/$', 'django.contrib.auth.views.password_reset_confirm', name='password_reset_confirm'),
    url(r'^reset/done/$', 'django.contrib.auth.views.password_reset_complete',name='password_reset_complete'),

    #url to retrieve file from ftp
    url(r'^retrieve_file/(?P<remote_folder>[^/]+)/(?P<remote_file>[^/]+)/', 'crpt201510.views.retrieve_file', name='retrieve_file'),

    # base url
    url(r'^$', 'crpt201510.views.index', name='index'),

    # url to index page
    url(r'^index/', 'crpt201510.views.index', name='index'),

    # url to upload assessment page
    url(r'^upload_assessment/', 'crpt201510.views.upload_assessment', name='upload_assessment'),

    # url to graphics page
    url(r'^graphics/(?P<assessment_id>\d+)/$', 'crpt201510.views.graphics', name='graphics'),

    # url to my_copyright page
    url(r'^my_copyright/$', 'crpt201510.views.my_copyright', name='my_copyright'),

    # url to admin app
    url(r'^admin/', include(admin.site.urls)),

    # Necessary to get widgets from admin running OK
    (r'^crpt201510/jsi18n/', 'django.views.i18n.javascript_catalog'),

)


