import sys
from ldap3 import Server, Connection, ALL, SUBTREE
from ldap3.core.exceptions import LDAPException, LDAPBindError


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

        self.__auth()

    def __auth(self):
        # TODO: retrieve info rom an '.env' file
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

    def __add_user(self):
        ldap_attr = {}
        ldap_attr['cn'] = "test user"
        ldap_attr['sn'] = "AD"

        user_dn = f"cn=testuser,cn=group1,{self.dc}"

        try:
            response = self.conn.add(dn=user_dn,
                                     object_class='inetOrgPerson',
                                     attributes=ldap_attr)
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
        # print(f"USER: {response}")

    def __del__(self):
        print("Destructor called")
        print("Closing connection")
        self.conn.unbind()
        self.conn = None


if __name__ == "__main__":
    m = Manager()
    # m.add_groups()
    m.add_users()
