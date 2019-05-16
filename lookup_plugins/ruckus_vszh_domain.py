from ansible.errors import AnsibleError, AnsibleParserError
from ansible.plugins.lookup import LookupBase

try:
    from __main__ import display
except ImportError:
    from ansible.utils.display import Display
    display = Display()

# When we execute with modul_utils directory on ANSIBLE_MODULUTILS
try:
    from ansible.module_utils.ruckus_vszh import vsz_api
# When we execute with python only
except ImportError:
    import sys
    sys.path.append('../module_utils/')
    from ruckus_vszh import vsz_api

class LookupModule(LookupBase):

    def run(self, terms, variables=None, **kwargs):

        #ret = variables['value']

        return 'from_plugin'


if __name__ == '__main__':
    test = LookupModule()
    test.run(None, variables={
        'value': 'hello'
    })