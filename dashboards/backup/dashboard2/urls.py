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

from django.conf.urls import url

from openstack_dashboard.dashboards.backup.dashboard2 import views


urlpatterns = [
    url(r'^$', views.IndexView.as_view(), name='index'),
    # url(r'^(?P<schedule_id>[^/]+)/edit-schedule$', views.JsonView.as_view(), name='edit-schedule'),
    url(r'^api/user-info', views.userInfo, name='userInfo'),
    url(r'^api', views.apiProxy, name='apiProxy'),
]
