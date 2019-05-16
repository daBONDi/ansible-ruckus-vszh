# ansible-ruckus-vszh

Ansible Module for managing Ruckus Virtual Smartzone Stuff

## ruckus_vszh_wlan_passphrase

Ensure WLAN Passphrase (PSK) for a specified WLAN

```yaml
- ruckus_vszh_wlan_passphrase:
    vsz_server: 10.0.0.23
    vsz_server_port: 8443
    vsz_user: myadminuser
    vsz_password: mysecretpassword
    ignore_ssl_validation: yes
    domain: customer1
    zone: customer1-zone1
    wlan: customer1-wlan2
    passphrase: start3456#
```
