#!/usr/bin/env python3

# Reference

import argparse
import json

EGRESS_PERM_ID = "IpPermissionsEgress"
INGRESS_PERM_ID = "IpPermissions"

class SecurityGroupParser(object):
    def __init__(self, security_group_json):
        self.security_groups = json.loads(security_group_json)
        self.parsed_groups = []

    def parse_groups(self):
        for security_group in self.security_groups["SecurityGroups"]:
            group_id = security_group["GroupId"]
            group_name = security_group["GroupName"]
            group_desc = security_group["Description"]
            vpc_id = security_group["VpcId"]
            tags = ",".join([str(x["Key"] + "=" + x["Value"]) for x in security_group["Tags"]])
            prefix = [vpc_id, group_id, group_name, group_desc, tags, "ingress"]

            # Ingress rules
            # Loop through all parsed ingress permissions
            for parsed_ingress_permission in self.parse_permissions(security_group[INGRESS_PERM_ID]):
                # Append output to parsed groups
                self.parsed_groups.append(prefix + parsed_ingress_permission)
            # Egress rules
            prefix[5] = "egress"
            # Loop through all parsed egress permissions
            for parsed_egress_permission in self.parse_permissions(security_group[EGRESS_PERM_ID]):
                # Append output to parsed groups
                self.parsed_groups.append(prefix + parsed_egress_permission)

    def parse_permissions(self, permissions_list:list):
        parsed_permissions = []
        # Get all host objects
        for permission in permissions_list:
            # Can return the group name, or drill down to root host entries
            network_groups = [str(x["CidrIp"]) for x in permission.get("IpRanges", [])]
            network_groups += [str(x["CidrIp"]) for x in permission.get("Ipv6Ranges", [])]
            network_groups += [str(x["UserId"]+"/"+x["GroupId"]) for x in permission.get("UserIdGroupPairs", [])]
            network_groups += [x["GroupName"] for x in permission.get("Groups", [])]
            #network_groups = self.get_root_networks(permission)
            # Get port ranges as strings
            from_port = str(permission.get("FromPort","any"))
            to_port = str(permission.get("ToPort","any"))
            if from_port == to_port:
                ports = to_port
            else:
                ports = from_port + "-" + to_port
            # Get protocols as strings
            ip_protocol = str(permission.get("IpProtocol","none"))
            if ip_protocol == "-1":
                ip_protocol = "any"
            # Add the rules to the output
            parsed_permissions.append([",".join([str(x) for x in network_groups]), ports, ip_protocol])
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
            for permission_group in group.get("Groups"):
                # Get the group definition
                permission_group_definition = [x for x in self.security_groups["SecurityGroups"] if x["GroupId"] == permission_group["GroupId"]][0]
                # Recurse
                sub_group_networks = self.get_root_networks_rec(permission_group_definition)

        return networks + group.get("IpRanges", []) + group.get("Ipv6Ranges", [])

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