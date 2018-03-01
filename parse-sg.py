#!/usr/bin/env python3

import argparse
import json

EGRESS_PERM_ID = "ipPermissionsEgress"
INGRESS_PERM_ID = "ipPermissions"

class SecurityGroupParser(object):
    def __init__(self, security_group_json):
        self.security_groups = json.loads(security_group_json)
        self.parsed_groups = []

    def parse_groups(self):
        for security_group in self.security_groups["securityGroupInfo"]:
            group_id = security_group["groupId"]
            group_name = security_group["groupName"]
            group_desc = security_group["groupDescription"]
            vpc_id = security_group["vpcId"]
            prefix = [vpc_id, group_id, group_name, group_desc, "ingress"]

            # Ingress rules
            # Loop through all parsed ingress permissions
            for parsed_ingress_permission in self.parse_permissions(security_group[INGRESS_PERM_ID]):
                # Append output to parsed groups
                self.parsed_groups.append(prefix + parsed_ingress_permission)
            # Egress rules
            prefix[4] = "egress"
            # Loop through all parsed egress permissions
            for parsed_egress_permission in self.parse_permissions(security_group[EGRESS_PERM_ID]):
                # Append output to parsed groups
                self.parsed_groups.append(prefix + parsed_egress_permission)

    def parse_permissions(self, permissions_list:list):
        parsed_permissions = []
        # Get all host objects
        for permission in permissions_list:
            # Can return the group name, or drill down to root host entries
            network_groups = permission.get("ipRanges", [])
            network_groups += permission.get("ipv6Ranges", [])
            network_groups += [x["groupName"] for x in permission.get("groups", [])]
            #network_groups = self.get_root_networks(permission)
            # Get port ranges as strings
            from_port = str(permission.get("fromPort","any"))
            to_port = str(permission.get("toPort","any"))
            if from_port == to_port:
                ports = to_port
            else:
                ports = from_port + "-" + to_port
            # Get protocols as strings
            ip_protocol = str(permission.get("ipProtocol","none"))
            # Add the rules to the output
            parsed_permissions.append([",".join(network_groups), ports, ip_protocol])
        # Return output
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
            for permission_group in group.get("groups"):
                # Get the group definition
                permission_group_definition = [x for x in self.security_groups["securityGroupInfo"] if x["groupId"] == permission_group["groupId"]][0]
                # Recurse
                sub_group_networks = self.get_root_networks_rec(permission_group_definition)

        return networks + group.get("ipRanges", []) + group.get("ipv6Ranges", [])

    def print_rules(self):
        for rule in self.parsed_groups:
            print("|".join(rule))

def main():

    # Set up arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("filename")
    args = parser.parse_args()

    # Read contents
    with open(args.filename, 'r') as infile:
        file_contents = infile.read()

    # Create parser
    aws_parser = SecurityGroupParser(file_contents)
    aws_parser.parse_groups()
    aws_parser.print_rules()
 
    return 0


if __name__ == "__main__":
    main()
