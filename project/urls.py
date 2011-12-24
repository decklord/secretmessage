from django.conf.urls.defaults import patterns, include, url
from api.application import SecretApi as Api
from jsonrpc import jsonrpc_site
import api.rpc
import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()
api = Api()


urlpatterns = patterns('',
        #(r'^api/services/', include('api.urls')),
        (r'^api/rpc/$', jsonrpc_site.dispatch),
        (r'^api/',include(api.urls)),
        (r'^qa/',include('qa.urls')),
        url(r'^admin/', include(admin.site.urls)),
)

if settings.DEBUG:
    urlpatterns += patterns('',
            (r'^'+settings.MEDIA_URL[1:]+'(?P<path>.*)$', 
               'django.views.static.serve', 
               {'document_root': settings.MEDIA_ROOT}),
            (r'^api/rpc-browse/$', 'jsonrpc.views.browse'),
        url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    )

urlpatterns += patterns('',
        (r'^',include('frontend.urls'))
)
