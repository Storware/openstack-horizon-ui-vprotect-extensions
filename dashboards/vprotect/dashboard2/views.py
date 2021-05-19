from django.views import generic
from django.http import HttpResponse, JsonResponse
import requests, yaml, json

CONFIG = yaml.safe_load(open('/usr/share/openstack-dashboard/openstack_dashboard/dashboards/vprotect/config.yaml', 'r'))
VPROTECT_API_URL = CONFIG['REST_API_URL']
USER = CONFIG['USER']
PASSWORD = CONFIG['PASSWORD']

class IndexView(generic.TemplateView):
    template_name = 'vprotect/dashboard2/index.html'


class JsonView(generic.TemplateView):
    def get(self, request):
        return JsonResponse(request.body.decode('utf-8'), safe=False)

def login():
    payload = {
        "login": CONFIG['USER'],
        "password": CONFIG['PASSWORD']
    }
    headers = {'content-type': 'application/json'}
    session = requests.Session()
    session.post(VPROTECT_API_URL + '/session/login', data=json.dumps(payload), headers=headers)
    return session


def is_json(myjson):
  try:
    json_object = json.dumps(myjson)
  except ValueError as e:
    return False
  return True

def apiProxy(request):
    url = request.build_absolute_uri()
    pathIndex = url.find("api")
    vprotectPath = url[pathIndex+3:]
    response = None
    headers = {'content-type': 'application/json'}
    queryParamSeparator = None

    if vprotectPath.find("?") == -1:
        queryParamSeparator = "?"
    else:
        queryParamSeparator = "&"

    path = VPROTECT_API_URL + vprotectPath + queryParamSeparator + "project-uuid=" + request.user.tenant_id

    if request.method == "GET":
        response = login().get(path)
    if request.method == "POST":
        response = login().post(path, request.body, headers=headers)
    if request.method == "PUT":
        response = login().put(path, request.body, headers=headers)
    if request.method == "DELETE":
        response = login().delete(path)

    if "download" in path:
        response2 = HttpResponse(response.content)
        response2['Content-Type'] = response.headers['Content-Type']
        response2['Content-Disposition'] = response.headers['Content-Disposition']
        return response2
    else:
        return JsonResponse(response.json(), status=response.status_code, safe=False)

def userInfo(request):
    payload = {
        "login": CONFIG['USER'],
        "password": CONFIG['PASSWORD']
    }
    headers = {'content-type': 'application/json'}
    response = login().post(VPROTECT_API_URL + '/session/login', json.dumps(payload), headers=headers)

    return JsonResponse(response.json(), status=response.status_code, safe=False)
