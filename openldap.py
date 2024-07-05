import sys
import hashlib
import logging
from ldap3 import Server, Connection, ALL, SUBTREE
from ldap3.core.exceptions import LDAPException, LDAPBindError


logging.basicConfig(level=logging.DEBUG)

# TODO: logging system


class Manager():
    conn = None

    def __init__(self, envfile=".env"):
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

        self.__auth()

    def __auth(self):
        # TODO: retrieve info from an '.env' file
        #       attention to dc fields
        """
        """
        if self.conn is None:
            try:
                # Provide the hostname and port number of the openLDAP
                server = Server(self.server_uri, get_info=ALL)

                # username and password can be configured during openldap setup
                connection = Connection(
                    server,
                    user=self.conn_str,
                    password='admin',
                    raise_exceptions=True,
                )

                bind_response = connection.bind() # Returns True or False
                print(bind_response)

                if bind_response is False:
                    print("Binding error !")
                    sys.exit(1)

            except LDAPBindError as e:
                print(e)
                sys.exit(1)

            self.conn = connection

    def __add_organizational_units(self, ou_name):
        ldap_attr = {
            'objectClass': ['top', 'organizationalUnit']
        }

        # make Organization Unit
        try:
            response = self.conn.add(
                f'ou={ou_name},{self.dc}',
                attributes=ldap_attr,
            )

        except LDAPException as e:
            response = (" The error is ", e)

        return response

    def __add_posixgroup(self, group_name, group_id):
        ldap_attr = {
            'objectClass': ['top', 'posixGroup'],
            'gidNumber': f'{group_id}',
        }

        try:
            response = self.conn.add(
                f'cn={group_name},ou={self.ou_groups},{self.dc}',
                attributes=ldap_attr,
            )

        except LDAPException as e:
            response = (" The error is ", e)

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
        logging.debug('DN: %s', dn)

        try:
            response = self.conn.add(
                dn,
                attributes=ldap_attr,
            )
        except LDAPException as e:
            response = e

        return response

    def add_groups(self, starting_gid=500, groups=('admin', 'users',)):
        """
        """
        response = self.__add_organizational_units(self.ou_groups)
        print(f"OU {self.ou_groups}: {response}")

        gid = starting_gid
        for g in groups:
            response = self.__add_posixgroup(g, gid)
            print(f"CN {g}: {response}")

            gid += 1


    def add_users(self):
        """
        """
        response = self.__add_organizational_units(self.ou_users)
        print(f"OU {self.ou_users}: {response}")

        for user in self.USERS:
            response = self.__add_user(**user)
            print(f"USER: {response}")

    def __del__(self):
        logging.info('Closing connection')
        self.conn.unbind()
        self.conn = None


if __name__ == "__main__":
    m = Manager()
    m.add_groups()
    m.add_users()
