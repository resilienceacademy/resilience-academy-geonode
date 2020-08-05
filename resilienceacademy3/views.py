import json
from django.conf import settings
from django.shortcuts import render
from django.views.generic.base import View

from geonode.utils import json_response
from geonode.utils import http_client

# from geonode.monitoring.views import MetricsFilter

class hello_json(View):
    def get(self,request,the_name, *args, **kwargs):
        filter=request.GET.get('filter',None)
        out = {}
        out['hello'] = the_name or 'world'
        if filter:
            out['filter']=filter
        return json_response(out)


def hello_html(request,the_name):
    out = {}
    out['hello'] = the_name or 'world'
    return render(request,'hello/hello_html.html',out)
def _fetch_wp_json():
    base_url = settings.BLOG_BASE_URL
    wp_json_url = base_url + "/wp-json/wp/v2/posts?_embed&page=1&per_page=3"
    response, content = http_client.request(wp_json_url, method='GET')
    _output_json = json.loads(content)
    for _item in _output_json:
        _item['image_url'] = _item['_embedded']['wp:featuredmedia'][0]['source_url']
    return {'wp_posts':_output_json}

def posts(request):
    return json_response(_fetch_wp_json())

def posts_html(request):
    wp_json = _fetch_wp_json()
    return render(request,'blog/posts.html',wp_json)

# def metric_countries(request, *args, **kwargs):
#     _monitoring_view = MetricDataView(request)
#     out = _monitoring_view.get(request)
#     return out





