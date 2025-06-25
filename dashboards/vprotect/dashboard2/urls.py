# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from django.urls import re_path
from openstack_dashboard.dashboards.vprotect.dashboard2 import views


urlpatterns = [
    re_path(r'^$', views.IndexView.as_view(), name='index'),
    # re_path(r'^(?P<schedule_id>[^/]+)/edit-schedule$', views.JsonView.as_view(), name='edit-schedule'),
    re_path(r'^api/user-info', views.userInfo, name='userInfo'),
    re_path(r'^api', views.apiProxy, name='apiProxy'),
]
