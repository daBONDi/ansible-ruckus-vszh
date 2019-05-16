# ansible-ruckus-vszh

Ansible Module for managing Ruckus Virtual Smartzone

## TODO

- [ ] Implement Lookup Filter to get domain/zone/wlan with regexp for eval/module usage

## ruckus_vszh_wlan_passphrase

Ensure WLAN Passphrase (PSK) for a specified WLAN

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
