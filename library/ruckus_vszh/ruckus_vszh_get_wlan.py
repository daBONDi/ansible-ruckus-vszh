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
module: ruckus_vszh_get_wlan.py
short_description: Module for query the ruckus VSZ-H for WLANs in specific Domain, Zone or WLAN Name
description:
    - 'Module for query the Ruckus VSZ-H or WLANs in specific Domain, Zone or WLAN Name.'
    - 'Used for other ruckus_vszh modules as information source.'
    - 'return a array of wlan data objects (see RETURNS)'
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
            - 'Regex of the vsz domain name to search for.'
        required: false
    zone:
        description:
            - 'Regex of the vsz zone name to search for.'
        required: false
    wlan:
        description:
            - 'Regex of the wlan name to search for.'
        required: false
notes:
    - 'Tested with VSZ Version: 3.6.2.0.222'
'''

EXAMPLES = r'''
- ruckus_vszh_get_wlan:
    vsz_server: 10.0.0.23
    vsz_server_port: 8443
    vsz_user: mysecretuser
    vsz_password: mysecretpassword
    ignore_ssl_validation: yes
    domain: ^customer
    zone: ^guest
    wlan: guest
    register: result
'''

RETURN = r'''
wlan:
    description: Array of WLAN objects
    return: On success
    type: complex
    contains:
        - wlan_id: Internal Id of the wlan
          wlan_name: Name of the wlan
          zone_id: Name of the zone
          zone_name: Name of the zone
          domain_id: Interal Id of the domain
          domain_name: Name of the domain
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
import re

def filter_regex_name(object_list, regex_filter_string):
    return filter(
        lambda x: (re.compile(regex_filter_string)).search(x['name']), object_list
        )

def easy_debug_output(query_result):
    # Debug Output
    format="{:<10} | {:<20} | {:<40} | {:<20} | {:<40} | {:<10}"
    print format.format("wlan_id","wlan_name","zone_id","zone_name","domain_id","domain_name")
    for w in query_result:
        print format.format(
            w['wlan_id'], 
            w['wlan_name'], 
            w['zone_id'], 
            w['zone_name'], 
            w['domain_id'], 
            w['domain_name'])

def run_module():

    # Setup Module
    module_args = dict(
        vsz_server=dict(type='str', required=True),
        vsz_server_port=dict(type='int', required=False, default=8443),
        vsz_user=dict(type='str', required=True),
        vsz_password=dict(type='str', required=True, no_log=True),
        use_ssl=dict(type='bool', required=False, default=True),
        ignore_ssl_validation=dict(type='bool', required=False, default=False),
        domain=dict(type='str', required=False),
        zone=dict(type='str', required=False),
        wlan=dict(type='str', required=False)
    )
    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

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

    query_result = []   # Holder for the Result object

    # Get all desired domains
    desired_domains=[]
    status, data = vsz.get_domains()
    if not status:
        module.fail_json(msg="api domain error: " + str(data))
    if(module.params['domain']):
        desired_domains = filter_regex_name(data, module.params['domain'])
    else:    
        desired_domains = data

    for domain in desired_domains:
        
        # Get Zones for this Domain
        status, data = vsz.get_rkszones(domain['id'])
        if not status:
            module.fail_json(msg="api rkszones error: " + str(data))
        if(module.params['zone']):
            desired_zones = filter_regex_name(data, module.params['zone'])
        else:
            desired_zones = data
        
        for zone in desired_zones:
            # Get the desired WLANs
            status, data = vsz.get_wlans(zone['id'])
            if not status:
                module.fail_json(msg="api wlan error:" + str(data))
            if(module.params['wlan']):
                desired_wlans = filter_regex_name(data, module.params['wlan'])
            else:
                desired_wlans = data
            
            # Now we got the filtered data, lets fill up result array
            for wlan in desired_wlans:
                object = {
                    "wlan_id" : wlan['id'],
                    "wlan_name": wlan['name'],
                    "zone_id": zone['id'],
                    "zone_name": zone['name'],
                    "domain_id": domain['id'],
                    "domain_name": domain['name']
                }
                query_result.append(object)

    #### only for debug output :-)
    # easy_debug_output(query_result)

    # Logout
    status, data = vsz.logout()
    if not status:
        module.fail_json(msg="api logout error: " + str(data))

    result = dict(
        changed = False,
        wlans = query_result
    )

    module.exit_json(**result)

if __name__ == '__main__':
    run_module()
