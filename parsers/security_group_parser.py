import json
<<<<<<< HEAD
from parsers.parser import AWSParser
=======
>>>>>>> d7d6df26e3185bfc0d5e1b6a15b8fe7d2a859276
from models.security_group import SecurityGroup
from models.ip_permission import IPPermission

EGRESS_PERM_ID = "IpPermissionsEgress"
INGRESS_PERM_ID = "IpPermissions"

class SecurityGroupParser(AWSParser):

    def parse(self):
        return self.parse_groups()

    def parse_groups(self):
        parsed_groups = []
        for security_group in self.json["SecurityGroups"]:
            # Build our security group
            cur_sg = SecurityGroup()
            cur_sg.group_id = security_group["GroupId"]
            cur_sg.name = security_group["GroupName"]
            cur_sg.description = security_group["Description"]
            cur_sg.vpc_id = security_group["VpcId"]
            cur_sg.tags = self.get_tag_dict(security_group.get("Tags", []))
            # Ingress rules
            for parsed_ingress_permission in self.parse_permissions(security_group[INGRESS_PERM_ID], "ingress"):
                cur_sg.ip_permissions.append(parsed_ingress_permission)
            # Egress rules
            for parsed_egress_permission in self.parse_permissions(security_group[EGRESS_PERM_ID], "egress"):
                cur_sg.ip_permissions.append(parsed_egress_permission)
            # Add to output list
            parsed_groups.append(cur_sg)
        return parsed_groups

    def parse_permissions(self, permissions_list:list, direction:str):
        parsed_permissions = []
        # Get all host objects
        for permission in permissions_list:
            cur_perm = IPPermission()
            cur_perm.direction = direction
            cur_perm.ipv4_ranges = permission.get("IpRanges", [])
            cur_perm.ipv6_ranges = permission.get("Ipv6Ranges", [])
            cur_perm.user_id_group_pairs = permission.get("UserIdGroupPairs", [])
            # Get port ranges as strings
            cur_perm.from_port = str(permission.get("FromPort","any"))
            cur_perm.to_port = str(permission.get("ToPort","any"))
            # Get protocols as strings
            cur_perm.protocol = str(permission.get("IpProtocol","none"))
            # Add the rules to the output
            parsed_permissions.append(cur_perm)
        return parsed_permissions

    def get_root_networks(self, group_list):
        networks = self.get_root_networks_rec(group_list)
        return networks

    # Takes a list of groups from a single permission, and walks the tree of nested groups to return
    # a list of ipRanges and ipv6Ranges which are referenced by all groups in the tree.
    def get_root_networks_rec(self, group):

        sub_group_networks = []

        if len(group.get("groups", [])) > 0:
            # Go through each group in the list
            for permission_group in group.get("Groups"):
                # Get the group definition
                permission_group_definition = [x for x in self.json["SecurityGroups"] if x["GroupId"] == permission_group["GroupId"]][0]
                # Recurse
                sub_group_networks = self.get_root_networks_rec(permission_group_definition)

        return networks + group.get("IpRanges", []) + group.get("Ipv6Ranges", [])

    def print_rules(self):
        for rule in self.parsed_groups:
            print("|".join(rule))

