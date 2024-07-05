import sys
import hashlib
import logging
from ldap3 import Server, Connection, ALL, SUBTREE
from ldap3.core.exceptions import LDAPException, LDAPBindError, LDAPEntryAlreadyExistsResult


logging.basicConfig(
    format='%(asctime)s - %(levelname)s: %(message)s',
    level=logging.INFO,
)


class Manager():
    """"""
    conn = None

    def __init__(self, envfile=".env"):
        logging.debug('Initializing connection')

        self.__envfile = envfile

        # TODO: load from .env

        self.server_uri = "ldap://localhost:389"
        self.dc = 'dc=example,dc=org'
        self.ou_groups = 'groups'
        self.ou_users = 'users'
        self.conn_str = f'cn=admin,{self.dc}'

        self.USERS = [
            {'user_id':'nv98001', 'first_name': 'nicolo', 'last_name': 'vescera', 'password': '1234patata', 'ou':self.ou_users, 'uid':1000, 'gid':501},
            {'user_id':'ff99003', 'first_name': 'fabrizio', 'last_name': 'fagiolo', 'password': '1234patata', 'ou':self.ou_users, 'uid':1001, 'gid':501},
            {'user_id':'mirko', 'first_name': 'mirko', 'last_name': 'mariotti', 'password': '1234patata', 'ou':self.ou_users, 'uid':1002, 'gid':500},
        ]

        logging.debug(
            'Loaded configs: server_uri: %s, dc: %s, ou_groups: %s, ou_users %s, conn_str: %s',
            self.server_uri,
            self.dc,
            self.ou_groups,
            self.ou_users,
            self.conn_str,
        )
        logging.debug('USERS: %s', self.USERS)

        self.__auth()

    def __auth(self):
        # TODO: retrieve info from an '.env' file
        #       attention to dc fields
        """
        """
        if self.conn is None:
            logging.debug("Connecting to %s", self.server_uri)

            try:
                # Provide the hostname and port number of the openLDAP
                server = Server(self.server_uri, get_info=ALL)
                logging.debug('Server: %s', server)

                # username and password can be configured during openldap setup
                connection = Connection(
                    server,
                    user=self.conn_str,
                    password='admin',
                    raise_exceptions=True,
                )
                logging.debug('Connection: %s', connection)

                bind_response = connection.bind() # Returns True or False
                logging.debug('Bind connection: %s', bind_response)

                if bind_response is False:
                    logging.error("Binding error !")
                    sys.exit(1)

            except LDAPBindError as e:
                logging.error(e)
                sys.exit(1)

            self.conn = connection
            logging.debug("Connection: %s", self.conn)

            logging.info("Successfully connected !")

    def __add_organizational_units(self, ou_name):
        ldap_attr = {
            'objectClass': ['top', 'organizationalUnit']
        }
        dn = f'ou={ou_name},{self.dc}'

        logging.debug("ADD REQ: dn: %s, attr: %s", dn, ldap_attr)

        try:
            response = self.conn.add(
                dn,
                attributes=ldap_attr,
            )
            logging.debug("Respone: %s", response)

        except LDAPEntryAlreadyExistsResult as e:
            logging.warning(e)
            response = "skip"
            # response = f"WARNING - {e}"

        except LDAPException as e:
            logging.error(e)
            sys.exit(1)

        return response

    def __add_posixgroup(self, group_name, group_id):
        ldap_attr = {
            'objectClass': ['top', 'posixGroup'],
            'gidNumber': f'{group_id}',
        }
        dn = f'cn={group_name},ou={self.ou_groups},{self.dc}'

        logging.debug("ADD REQ: dn: %s, attr: %s", dn, ldap_attr)

        try:
            response = self.conn.add(
                dn,
                attributes=ldap_attr,
            )
            logging.debug("Respone: %s", response)

        except LDAPEntryAlreadyExistsResult as e:
            logging.warning(e)
            response = "skip"
            # response = f"WARNING - {e}"

        except LDAPException as e:
            logging.error(e)
            sys.exit(1)

        return response

    def __add_user(self, user_id:str, first_name, last_name, password:str, ou, uid:int, gid:int):
        common_name = f'{first_name} {last_name}'

        ldap_attr = {
            'givenName': first_name,
            'sn': last_name,
            'cn': common_name,
            'uid': user_id,
            'userPassword': hashlib.md5(password.encode()).hexdigest(), # TODO: should be encoded ??
            'uidNumber': f'{uid}',
            'gidNumber': f'{gid}',
            'homeDirectory': f'/home/user/{user_id}',
            'objectClass': ['inetOrgPerson', 'posixAccount', 'top'],
        }
        dn = f'cn={common_name},ou={ou},{self.dc}'

        logging.debug("ADD REQ: dn: %s, attr: %s", dn, ldap_attr)

        try:
            response = self.conn.add(
                dn,
                attributes=ldap_attr,
            )
            logging.debug("Respone: %s", response)

        except LDAPEntryAlreadyExistsResult as e:
            logging.warning(e)
            response = "skip"
            # response = f"WARNING - {e}"

        except LDAPException as e:
            logging.error(e)
            sys.exit(1)

        return response

    def add_groups(self, starting_gid=500, groups=('admin', 'users',)):
        """
        """
        response = self.__add_organizational_units(self.ou_groups)
        logging.info("OU %s: %s", self.ou_groups, response)

        gid = starting_gid
        for g in groups:
            response = self.__add_posixgroup(g, gid)
            logging.info("CN %s: %s", g, response)

            gid += 1


    def add_users(self):
        """
        """
        response = self.__add_organizational_units(self.ou_users)
        logging.info("OU %s: %s", self.ou_users, response)

        for user in self.USERS:
            response = self.__add_user(**user)
            logging.info("USER: %s", response)

    def __del__(self):
        logging.info('Closing connection')
        self.conn.unbind()
        self.conn = None


if __name__ == "__main__":
    m = Manager()
    m.add_groups()
    m.add_users()
