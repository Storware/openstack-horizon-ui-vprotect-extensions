import json
import requests
import yaml
from django.http import HttpResponse, JsonResponse
from django.views import generic

CONFIG = yaml.safe_load(open('/usr/share/openstack-dashboard/openstack_dashboard/dashboards/vprotect/config.yaml', 'r'))
VPROTECT_API_URL = CONFIG['REST_API_URL']
USER = CONFIG['USER']
PASSWORD = CONFIG['PASSWORD']
HTTP_STATUS_NO_CONTENT = 204


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
    session.post(VPROTECT_API_URL + '/session/login', data=json.dumps(payload), headers=headers, verify=False)
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
    elif request.method == "POST":
        response = login().post(path, request.body, headers=headers)
    elif request.method == "PUT":
        response = login().put(path, request.body, headers=headers)
    elif request.method == "DELETE":
        response = login().delete(path)

    if is_endpoint_contentable(path):
        response2 = HttpResponse(response.content)
        response2['Content-Type'] = response.headers['Content-Type']
        response2['Content-Disposition'] = response.headers['Content-Disposition']        
        response2['3rd_party'] = 'HORIZON'
        response2['3rd_party_project'] = request.user.tenant_id
        return response2
    elif response.status_code != HTTP_STATUS_NO_CONTENT and is_json_content(response):
        jsonResponse = JsonResponse(response.json(), status=response.status_code, safe=False)
        if 'X-Total-Count' in response.headers:
            jsonResponse['X-Total-Count'] = response.headers['X-Total-Count']
        jsonResponse['3rd_party'] = 'HORIZON'
        jsonResponse['3rd_party_project'] = request.user.tenant_id
        return jsonResponse
    else:
        return HttpResponse(response.content)

def is_endpoint_contentable(url):
    return any(elem in url for elem in ['download', 'report-pdf', 'report-html'])

def is_json_content(response):
    return "content-type" in response.headers and response.headers["content-type"].strip().startswith("application/json")


def userInfo(request):
    payload = {
        "login": CONFIG['USER'],
        "password": CONFIG['PASSWORD']
    }
    headers = {'content-type': 'application/json'}
    response = login().post(VPROTECT_API_URL + '/session/login', json.dumps(payload), headers=headers)

    return JsonResponse(response.json(), status=response.status_code, safe=False)
