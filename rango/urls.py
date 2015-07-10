from django.conf.urls import patterns, url
from rango import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = patterns('', 
	url(r'^$', views.index, name='index'), 
	url(r'^about/', views.about, name='about'), 
	url(r'^category/(?P<category_name_slug>[\w\-]+)/$', views.category, name='category'),)

# this is for the urlpatterns with respect to static folder information. 
if not settings.DEBUG:
	urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
