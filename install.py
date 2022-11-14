
#!/usr/bin/env bash

import os
import shutil
import sys
import yaml
import requests, zipfile, io
from distutils.dir_util import copy_tree


CONFIG_PATH = 'dashboards/vprotect/config.yaml'
RELEASES_API = 'https://api.github.com/repos/Storware/ovirt-engine-ui-vprotect-extensions/releases'
VERSION_DATA = None


def install_dashboard_menu(ver = '5.1'):
    try:
        shutil.copyfile('dashboard_'+ver+'.py', 'dashboards/vprotect/dashboard.py')
    except FileNotFoundError:
        raise FileNotFoundError('Plugin version not recognised - release name should start with "v5.1" or "v5.0".')
    # other solution in case of different versions in the future:
    #   if ver not in ['5.1', '5.0']:
    #       shutil.copyfile('dashboard_5.1.py', 'dashboards/vprotect/dashboard.py')

def update_variable(state, variable):
    with open(CONFIG_PATH) as f:
        doc = yaml.safe_load(f)

    doc[variable] = state

    with open(CONFIG_PATH, 'w') as f:
        yaml.safe_dump(doc, f, default_flow_style=False)

def getReleaseLabel(release):
    return release['name'][1:]

if len(sys.argv) >= 2:
    update_variable(sys.argv[1], 'REST_API_URL')

if len(sys.argv) >= 3:
    update_variable(sys.argv[2], 'USER')

if len(sys.argv) >= 4:
    update_variable(sys.argv[3], 'PASSWORD')

versions = requests.get(RELEASES_API)
versionsNames = list(map(getReleaseLabel, versions.json()))

# If the version of package is provided
if len(sys.argv) >= 5:
    index = 0
    if sys.argv[4] != "latest":
        result = next(x for x in versionsNames if sys.argv[4] in x)
    else:
        result = versionsNames[0]
    index = versionsNames.index(result)

    if versions.json()[index].get('message'):
        print(versions.json()[index]['message'])
    else:
        install_dashboard_menu(result[0:3])
        VERSION_DATA = versions.json()[index]
else:
    result = versionsNames[0]
    if result:
        install_dashboard_menu(result[0:3])
        VERSION_DATA = versions.json()[0]

if VERSION_DATA.get('assets'):
    openstackUrl = VERSION_DATA['assets'][0]['browser_download_url']
    package = requests.get(openstackUrl)

    z = zipfile.ZipFile(io.BytesIO(package.content))
    z.extractall("dashboards/vprotect/static/vprotect")
    z.extractall("/usr/share/openstack-dashboard/static/vprotect")

    path = '/usr/share/openstack-dashboard/openstack_dashboard/enabled'
    isExist = os.path.exists(path)
    if not isExist:
        os.makedirs(path)

    copy_tree('dashboards/vprotect/', '/usr/share/openstack-dashboard/openstack_dashboard/dashboards/vprotect/')
    shutil.copyfile('enabled/_50_vprotect.py', '/usr/share/openstack-dashboard/openstack_dashboard/enabled/_50_vprotect.py')
