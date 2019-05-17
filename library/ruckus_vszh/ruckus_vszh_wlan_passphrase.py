#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# @author: David Baumann(me@davidbaumann.at)
#
# module_check: supported
#
# Copyright: (c) 2019, David Baumann <me@davidbaumann.at>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

ANSIBLE_METADATA = {'metadata_version': '1.0',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = r'''
---
module: 'ruckus_vszh_wlan_passphrase.py'
short_description: 'Module for setting the passphrase(PSK) for a specific WLAN'
description:
    - 'Module for setting the passphrase(PSK) for a specific WLAN'
author: 'David Baumann (@daBONDi) <me@davidbaumann.at>'
options:
    vsz_server:
        description:
            - 'IP or FQDN of the Ruckus VSZ-H server.'
        required: true
    vsz_server_port:
        description: 
            - 'TCP port for the Ruckus VSZ-H server.'
        required: false
        default: 8443
    vsz_user:
        description: 
            - 'User for accessing the Ruckus VSZ-H Public API.'
        required: true
    vsz_password:
        description: 
            - 'Password for accessing the Ruckus VSZ-H Public API.'
    ignore_ssl_validation:
        description: 
            - 'Ignore SSL certificate validation check.'
        required: false
        default: false
    use_ssl:
        description:
            - 'User https for accessing the Ruckus VSZ-H Public API.'
        required: false
        default: true
    domain:
        description:
            - 'vsz domain'
        required: true
    zone:
        description:
            - 'zone name'
        required: true
    wlan:
        description:
            - 'wlan name'
        required: true
    passphrase:
        description:
            - 'Password for the WLAN (PSK)'
        requried: true
notes:
    - 'Tested with VSZ Version: 3.6.2.0.222'
'''

EXAMPLES = r'''
- ruckus_vszh_wlan_passphrase:
    vsz_server: 10.0.0.23
    vsz_user: myadminuser
    vsz_password: mysecretpassword
    ignore_ssl_validation: yes
    domain: customer1
    zone: customer1-zone1
    wlan: customer1-wlan2
    passphrase: start3456#
'''

RETURN=r'''
'''

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.urls import Request, SSLValidationError

# When we execute with modul_utils directory on ANSIBLE_MODULUTILS
try:
    from ansible.module_utils.ruckus_vszh import vsz_api
# When we execute with python only
except ImportError:
    import sys
    sys.path.append('../../module_utils/')
    from ruckus_vszh import vsz_api


import json
import urllib2

def run_module():

    # Setup Module
    module_args = dict(
        vsz_server=dict(type='str', required=True),
        vsz_server_port=dict(type='int', required=False, default=8443),
        vsz_user=dict(type='str', required=True),
        vsz_password=dict(type='str', required=True, no_log=True),
        use_ssl=dict(type='bool', required=False, default=True),
        ignore_ssl_validation=dict(type='bool', required=False, default=False),
        domain=dict(type='str', required=True),
        zone=dict(type='str', required=True),
        wlan=dict(type='str', required=True),
        passphrase=dict(type='str', required=True, no_log=True),
    )
    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    changed = False

    vsz = vsz_api(
        module.params['vsz_server'],
        module.params['vsz_user'],
        module.params['vsz_password'],
        module.params['vsz_server_port'],
        module.params['use_ssl'],
        module.params['ignore_ssl_validation']
    )

    # Login
    status, data = vsz.login()
    if not status:
        module.fail_json(msg="api login error: " + str(data))

    # Get domain id and fail if requested domain not exist
    status, data = vsz.get_domain_id(module.params['domain'])
    if not status:
        module.fail_json(msg="api get domain error: " + str(data))
    domain_id = data
 
    # Get zone id and fail if requested zone not exists
    status, data = vsz.get_rkszone_id(module.params['zone'], domain_id)
    if not status:
        module.fail_json(msg="api get zones error: " + str(data))
    zone_id = data

    # Get wlan id and fail if requested wlan not exists
    status, data = vsz.get_wlan_id(zone_id, module.params['wlan'])
    if not status:
        module.fail_json(msg="api get wlan error: " + str(data))
    wlan_id = data


    # Now we fetch the current settings from wlan
    status, data = vsz.get_wlan_settings(zone_id, wlan_id)
    if not status:
        module.fail_json(msg="api get wlan settings error: " + str(data))
    
    current_wlan_settings = data
    
    if not 'encryption' in current_wlan_settings:
        module.fail_json(msg="api get wlan settings error: no encryption settings on api response!")

    current_encryption_settings = current_wlan_settings['encryption']
    if not current_encryption_settings['passphrase'] == module.params['passphrase']:
        if(not module.check_mode):
            # We realy change here
            new_encryption_settings = current_encryption_settings
            new_encryption_settings['passphrase'] = module.params['passphrase']
            result, data = vsz.set_wlan_encryption(zone_id, wlan_id, new_encryption_settings)
            if not result:
                module.fail_json(msg="api wlan encryption setting: error on applying new settings " + data)

        changed = True

    # Logout
    status, data = vsz.logout()
    if not status:
        module.fail_json(msg="api logout error: " + str(data))

    result = dict(
        changed = changed
    )

    module.exit_json(**result)

if __name__ == '__main__':
    run_module()
