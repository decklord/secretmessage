from django.conf.urls.defaults import patterns, include, url
import views

urlpatterns = patterns('',
        (r'^qunit$', views.qunit),
        (r'^echo$', views.echo)
)

