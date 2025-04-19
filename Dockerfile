FROM ubuntu:22.04
ENV DEBIAN_FRONTEND=noninteractive

RUN apt update
RUN apt upgrade -y
RUN apt install openstack-dashboard -y
RUN apt clean

RUN echo "\
OPENSTACK_HOST = 'controller'\n\
ALLOWED_HOSTS = ['one.example.com', 'two.example.com']\n\
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'\n\
CACHES = {\n\
    'default': {\n\
        'BACKEND': 'django.core.cache.backends.memcached.PyMemcacheCache',\n\
        'LOCATION': 'controller:11211',\n\
    }\n\
}\n\
OPENSTACK_KEYSTONE_URL = 'http://%s/identity/v3' % OPENSTACK_HOST\n\
OPENSTACK_API_VERSIONS = {\n\
    'identity': 3,\n\
    'image': 2,\n\
    'volume': 3,\n\
}\n\
OPENSTACK_KEYSTONE_DEFAULT_DOMAIN = 'Default'\n\
" > /etc/openstack-dashboard/local_settings.py

RUN a2enmod wsgi 
RUN ln -sf /etc/apache2/conf-available/openstack-dashboard.conf /etc/apache2/conf-enabled/

EXPOSE 80

CMD service memcached start && apache2ctl -D FOREGROUND
