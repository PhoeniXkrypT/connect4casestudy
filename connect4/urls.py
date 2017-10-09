from django.conf.urls import url
import views

urlpatterns = [
    url(r'^login/$', views.login, name='login'),
    url(r'^signup/$', views.signup, name='signup'),
    url(r'^logout/$', views.logout, name='logout'),
    url(r'^games/$', views.games, name='games'),
    url(r'^play/$', views.play, name='play'),
]
