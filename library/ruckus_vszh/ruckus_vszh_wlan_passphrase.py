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
        changed = changed,
        domain_id = domain_id,
        zone_id = zone_id,
        wlan_id = wlan_id
    )

    module.exit_json(**result)

if __name__ == '__main__':
    run_module()
