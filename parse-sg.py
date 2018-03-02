#!/usr/bin/env python3

# Reference https://docs.aws.amazon.com/cli/latest/reference/ec2/describe-security-groups.html

import argparse
import json

EGRESS_PERM_ID = "IpPermissionsEgress"
INGRESS_PERM_ID = "IpPermissions"

class SecurityGroup(object):
    def __init__(self):
        self.description = ""
        self.name = ""
        self.owner_id = ""
        self.group_id = ""
        self.tags = []
        self.vpc_id = ""
        self.ip_permissions = []

class IPPermission(object):
    def __init__(self):
        self.direction = "" # ingress/egress
        self.from_port = None
        self.to_port = None
        self.protocol = ""
        self.ipv4_ranges = [] # dict of CidrIp and Description
        self.ipv6_ranges = [] # dict of CidrIp6 and Description
        self.prefix_list_ids = [] # dict of PrefixListId and Description
        self.user_id_group_pairs = [] # dict of GroupId, GroupName, UserId, Description, PeeringStatus, VpcId, VpcPeeringConnectionId

class VPC(object):
    def __init__(self):
        self.vpc_id = ""
        self.tags = []
        self.state = ""
        self.is_default = ""
        self.cidr = ""
        self.assigned_subnets = []


class SecurityGroupPrinter(object):
    def print_csv(self, security_group:SecurityGroup, vpcs=None):
        # if protocol = -1 print any
        # if from_port and to_port are the same just print from_port, if they're different print "from_port-to_port"
        return None


class VPCParser(object):
    def __init__(self, vpc_json:str):
        self.vpc_json = json.loads(vpc_json)
        
    def parse_vpcs(self):
        parsed_vpcs = []
        for vpc in self.vpc_json["Vpcs"]:
            cur_vpc = VPC()
            cur_vpc.vpc_id = vpc["VpcId"]
            cur_vpc.tags = vpc.get("Tags",[])
            cur_vpc.state = vpc["State"]
            cur_vpc.is_default = vpc["IsDefault"]
            cur_vpc.cidr = vpc["CidrBlock"]
            cur_vpc.assigned_subnets = vpc["CidrBlockAssociationSet"]
            parsed_vpcs.append(cur_vpc)
        return parsed_vpcs
        

class SecurityGroupParser(object):
    def __init__(self, security_group_json):
        self.security_groups = json.loads(security_group_json)

    def parse_groups(self):
        parsed_groups = []
        for security_group in self.security_groups["SecurityGroups"]:
            # Build our security group
            cur_sg = SecurityGroup()
            cur_sg.group_id = security_group["GroupId"]
            cur_sg.name = security_group["GroupName"]
            cur_sg.description = security_group["Description"]
            cur_sg.vpc_id = security_group["VpcId"]
            cur_sg.tags = security_group.get("Tags", [])
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
    parser.add_argument("--groups", help="Path to file containing describe-security-groups")
    parser.add_argument("--vpcs", help="Path to file containing describe-vpcs")
    args = parser.parse_args()

    # Read contents
    with open(args.groups, 'r') as describe_sg_file:
        sg_description = describe_sg_file.read()

    # Create parser
    sg_parser = SecurityGroupParser(sg_description)
    parsed_sgs = sg_parser.parse_groups()

    parsed_vpcs = None
    if args.vpcs:
        with open(args.vpcs, 'r') as describe_vpc_file:
            vpc_description = describe_vpc_file.read()
        vpc_parser = VPCParser(vpc_description)
        parsed_vpcs = vpc_parser.parse_vpcs()

    sg_printer = SecurityGroupPrinter().print_csv(parsed_sgs, parsed_vpcs)
 
    return 0


if __name__ == "__main__":
    main()
