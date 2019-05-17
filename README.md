# ansible-ruckus-vszh

Ansible module for managing Ruckus Virtual Smartzone

**TODO::**
 - [ ] More Testing
 - [ ] Awsome ansible module docs

## ruckus_vszh_get_wlan

Query the WSZ for wlans with regex and return it under the object 'wlans'

### Parameters

| Parameter | Description | Required  | Default |
| --------- | ----------- | --------- | ------- |
| vsz_server        | FQDN or IP Address of the Ruckus VSZ Server | Yes | |
| vsz_server_port   | TCP Port | no | 8443 |
| vsz_user          | API User | yes | | 
| vsz_password      | Password | yes | | 
| use_ssl | Use HTTPS for API Access | no | True |
| ignore_ssl_validation | Ignore SSL Certificate Validateion | no | False |
| domain | Regex - VSZ Domain Name | no | |
| zone | Regex - VSZ Zone Name | no | |
| wlan | Regex - VSZ WLAN Name | no | |

### Response

```json
{ 
    "wlans": [
        {
            "wlan_id": "<Value>",
            "wlan_name": "<Value>",
            "zone_id": "<Value>",
            "zone_name": "<Value>",
            "domain_id": "<Value>",
            "domain_name": "<Value>"
        }
    ]
}
``` 

### Example

```yaml
- ruckus_vszh_get_wlan:
    vsz_server: 10.0.0.23
    vsz_server_port: 8443
    vsz_user: mysecretuser
    vsz_password: mysecretpassword
    ignore_ssl_validation: yes
    
    # Lets get all wlans 
    # - for domain "customer1*" 
    # - with zone "guest*" 
    # - and wlans with '*guest*'
    domain: ^customer
    zone: ^guest
    wlan: guest
    register: result

- debug:
    msg: "{{ item.domain_name }} {{ item.zone_name }} {{ item.wlan_name }}"
    with_items: result.wlans
``` 

## ruckus_vszh_wlan_passphrase

Ensure wlan passphrase(PSK) for a specified wLAN

### Parameters

| Parameter | Description | Required  | Default |
| --------- | ----------- | --------- | ------- |
| vsz_server        | FQDN or IP Address of the Ruckus VSZ Server | Yes | |
| vsz_server_port   | TCP Port | no | 8443 |
| vsz_user          | API User | yes | | 
| vsz_password      | Password | yes | | 
| use_ssl | Use HTTPS for API Access | no | True |
| ignore_ssl_validation | Ignore SSL Certificate Validateion | no | False |
| domain | VSZ Domain Name | yes | |
| zone | VSZ Zone Name | yes | |
| wlan | VSZ WLAN Name | yes | |
| passphrase | VSZ WLAN Passphrase(PSK) | yes | |

### Example

```yaml
- ruckus_vszh_wlan_passphrase:
    vsz_server: 10.0.0.23
    vsz_user: myadminuser
    vsz_password: mysecretpassword
    ignore_ssl_validation: yes
    domain: customer1
    zone: customer1-zone1
    wlan: customer1-wlan2
    passphrase: start3456#
```
