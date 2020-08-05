# -*- coding: utf-8 -*-
#########################################################################
#
# Copyright (C) 2017 OSGeo
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
#########################################################################

from django.conf.urls import url, include
from django.views.generic import TemplateView

from geonode.urls import urlpatterns
from geonode.monitoring import register_url_event

from resilienceacademy3 import views

urlpatterns += [
## include your urls here
    url(r'^api/posts/$',views.posts,name="wp_posts"),
    url(r'^posts/$',views.posts_html,name="wp_posts_html"),
    url(r'^api/hello/(?P<the_name>[^/]*)$', views.hello_json.as_view(), name="hello_json"),
    url(r'^hello/(?P<the_name>[^/]*)$',views.hello_html,name="hello_html"),
    # url(r'^api/stats/countries/$',views.metric_countries,name="stats_coutries"),
]

homepage = register_url_event()(TemplateView.as_view(template_name='site_index.html'))

urlpatterns = [
    url(r'^/?$',
        homepage,
        name='home'),
  url(r'^contact-us/$',
        TemplateView.as_view(template_name='contact_us.html'),
        name='contact-us'),
    url(r'^term-of-use/$',
        TemplateView.as_view(
            template_name='terms_use.html'),
        name='term-of-use'),
    url(r'^get-started/$',
        TemplateView.as_view(template_name='get_started.html'),
        name='get-started'),
    url(r'^crd-team/$',
        TemplateView.as_view(template_name='crd_team.html'),
        name='crd-team'),
 ] + urlpatterns
