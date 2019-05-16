from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.urls import Request, SSLValidationError

import json
import urllib2


class vsz_api:

    api_endpoint_url = ''
    __api_user = ''
    __api_password = ''

    __request = None    # Holder for Request Object
    __ignore_ssl_validation = True

    __ansible_module = None

    def __init__(self, server, user, password, server_port=8443, use_ssl=True, ignore_ssl_validation=True):

        # Set api endpoint url
        if use_ssl:
            self.api_endpoint_url = self.api_endpoint_url + 'https://'
        else:
            self.api_endpoint_url = self.api_endpoint_url + 'http://'

        self.api_endpoint_url = self.api_endpoint_url + \
            server + ':' + str(server_port) + "/wsg/api/public"

        self.__api_password = password
        self.__api_user = user

        self.__ignore_ssl_validation = ignore_ssl_validation

        self.__request = Request()

    def get_domain_id(self, domain_name):

        fetch_domain_result, data = self.get_domains()
        if not fetch_domain_result:
            return False, data
        
        for domain in data:
            if domain_name == domain['name']:
                return True, domain['id']
        
        # No domain found
        return False, "domain with name '" + domain_name + "' not found!"


    def get_domains(self):
        return self.__return_api_list(
            *(self.__api_call('GET','/v6_0/domains?listSize=9999&recusively=True'))
        )

    def get_rkszone_id(self, zone_name, domain_id):
        fetch_zone_result, data = self.get_rkszones(domain_id)
        if not fetch_zone_result:
            return False, data
        
        for zone in data:
            if zone_name == zone['name']:
                return True, zone['id']
        
        # Zone not found
        return False, "zone with name '" + zone_name + "' not found!"

    def get_rkszones(self, domain_id):
        return self.__return_api_list(
            *(self.__api_call('GET','/v6_0/rkszones?listSize=9999&domainId=' + domain_id))
        )

    def set_wlan_encryption(self, zone_id, wlan_id, wlan_encryption_settings):
        data = {
            "method" : wlan_encryption_settings['method'],
            "passphrase" : wlan_encryption_settings['passphrase']
        }
        return self.__api_call('PATCH','/v4_0/rkszones/' + zone_id + '/wlans/' + wlan_id  + '/encryption', data=json.dumps(data))
        

    def get_wlan_settings(self, zone_id, wlan_id):
        result, data = self.__api_call('GET','/v4_0/rkszones/' + zone_id + '/wlans/' + wlan_id)
        return result, data

    def get_wlan_id(self, zone_id, wlan_name):
        fetch_wlan_result, data = self.get_wlans(zone_id)
        if not fetch_wlan_result:
            return False, data
        
        for wlan in data:
            if wlan_name == wlan['name']:
                return True, wlan['id']

        # Wlan not found
        return False, "wlan with name '" + wlan_name + "' not found!"
    

    def get_wlans(self, zone_id):
        return self.__return_api_list(
            *(self.__api_call('GET','/v6_0/rkszones/' + zone_id + '/wlans?listSize=99999'))
        )


    def login(self):
        data = dict(
            username=self.__api_user,
            password=self.__api_password,
            timeZoneUtcOffset="+01:00"
        )

        return self.__api_call(
            'POST','/v6_0/session', 
            data=json.dumps(data),
        )

    def logout(self):
        return self.__api_call(
                'DELETE','/v6_0/session'
            )
    

    # return list object of json response or pass error
    def __return_api_list(self,result,data):
        if not result:
            return result, data
        return result, data['list']

    # execute api calls
    def __api_call(self, http_method, api_method, data=None):
        if(type(data) is dict):
            data = json.dumps(data)
        try:
            request_result = self.__request.open(
                http_method, 
                (self.api_endpoint_url + api_method), 
                data = data,
                headers= {
                    "Content-Type": "application/json",
                    "Accept":"application/json"
                },
                validate_certs = not self.__ignore_ssl_validation
            )
        except urllib2.HTTPError as err:
            return False, err.msg
        except urllib2.URLError as err:
            return False, err.reason.strerror
        except SSLValidationError as err:
            return False, err.message
        except:
            return False, "unknown urllib2 exception"

        data = request_result.read()
        if data:
            return True, json.loads(data)

        return True, request_result.msg

def run_module():
    module_args = dict(
        vsz_server=dict(type='str', required=True),
        vsz_server_port=dict(type='int', required=False, default=8443),
        vsz_user=dict(type='str', required=True),
        vsz_password=dict(type='str', required=True, no_log=True),
        use_ssl=dict(type='bool', required=False, default=True),
        ignore_ssl_validation=dict(type='bool', required=False, default=True),
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


def main():
    run_module()


if __name__ == '__main__':
    main()
