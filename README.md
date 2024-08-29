# openLDAP 🐳

openLDAP's docker compose configuration

## Settings

Create a `.env` file with the following vars:

```env
LDAP_IP=
PROJECT=
DOMAIN=
ADMIN_PASSWORD=
CONFIG_PASSWORD=
READONLY_USER_USERNAME=
READONLY_USER_PASSWORD=
LDAPADMIN_IP=
```

An example could be:


```env
LDAP_IP=10.1.0.10
PROJECT=Example.org
DOMAIN=example.org
ADMIN_PASSWORD=admin
CONFIG_PASSWORD=config
READONLY_USER_USERNAME=readonly
READONLY_USER_PASSWORD=readonly
LDAPADMIN_IP=10.1.0.11
```
