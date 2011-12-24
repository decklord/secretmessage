
from django.conf.urls.defaults import patterns, include, url
import views

urlpatterns = patterns('',
        (r'^$', views.home),
        (r'^admin_message/$', views.admin_message),
        (r'^message/(\w+)/$', views.message),
        #(r'^login$', views.login),
)
