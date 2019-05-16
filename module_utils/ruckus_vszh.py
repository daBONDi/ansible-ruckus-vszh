from ansible.module_utils.urls import Request, SSLValidationError

import json
import urllib2


class vsz_api:

    api_endpoint_url = ''
    __api_user = ''
    __api_password = ''

    __request = None
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
