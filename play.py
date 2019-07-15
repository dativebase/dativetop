import pprint

import dativetop.client.dativetop as client
import dativetop.constants as c
import dativetop.client.domain as domain
import dativetop.getsettings as getsettings
import dativetop.introspect as di


#DATIVETOP_URL = 'http://127.0.0.1:6543/'
DATIVETOP_URL = 'http://127.0.0.1:5676/'
DATIVE_URL = 'http://127.0.0.1:5678/'
OLD_URL = 'http://127.0.0.1:5679/'


dativetop_service = client.DativeTopService(url=DATIVETOP_URL)
aol = client.get(dativetop_service)
print(aol)  # should be empty


declared_old_service, err1 = domain.construct_old_service(url=OLD_URL)
declared_dative_app, err2 = domain.construct_dative_app(url=DATIVE_URL)
print(declared_old_service)
print(declared_dative_app)


dativetop_settings = getsettings.get_settings(config_path=c.CONFIG_PATH)
print(dativetop_settings)

old_instances = []

for oi_dict in di.introspect_old_instances(dativetop_settings):
    pprint.pprint(oi_dict)
    slug = oi_dict['db_file_name']
    old_instance = domain.construct_old_instance(
            slug=slug, url=f'{OLD_URL}{slug}/',)
    pprint.pprint(old_instance)


# aol = client.get(dativetop_service)
