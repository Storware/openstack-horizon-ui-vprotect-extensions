
#!/usr/bin/env bash

import shutil
import sys
import yaml
import requests, zipfile, io
from distutils.dir_util import copy_tree
import os
from pick import pick


def update_variable(state, variable):
    with open(CONFIG_PATH) as f:
        doc = yaml.safe_load(f)

    doc[variable] = state

    with open(CONFIG_PATH, 'w') as f:
        yaml.safe_dump(doc, f, default_flow_style=False)

def getReleaseLabel(release):
    return release['name'] + " " + release['body']

CONFIG_PATH = 'dashboards/vprotect/config.yaml'

if len(sys.argv) >= 2:
    update_variable(sys.argv[1], 'REST_API_URL')

if len(sys.argv) >= 3:
    update_variable(sys.argv[2], 'USER')

if len(sys.argv) >= 4:
    update_variable(sys.argv[3], 'PASSWORD')

versions = requests.get("https://api.github.com/repos/Storware/ovirt-engine-ui-vprotect-extensions/releases")
versionsNames = map(getReleaseLabel, versions.json())

option, index = pick(list(versionsNames), "Select a version", indicator='=>')

if option:
    downloadPath = versions.json()[index]['assets'][0]['browser_download_url']
    r = requests.get("https://github.com/Storware/ovirt-engine-ui-vprotect-extensions/releases/download/openstack/openstack.zip")

    z = zipfile.ZipFile(io.BytesIO(r.content))
    z.extractall("dashboards/vprotect/static/vprotect")
    z.extractall("/usr/share/openstack-dashboard/static/vprotect")

    path = '/usr/share/openstack-dashboard/openstack_dashboard/enabled'
    isExist = os.path.exists(path)
    if not isExist:
        os.makedirs(path)

    copy_tree('dashboards/vprotect/', '/usr/share/openstack-dashboard/openstack_dashboard/dashboards/vprotect/')
    shutil.copyfile('enabled/_50_vprotect.py', '/usr/share/openstack-dashboard/openstack_dashboard/enabled/_50_vprotect.py')
