#!/usr/bin/env python3

# Reference https://docs.aws.amazon.com/cli/latest/reference/ec2/describe-security-groups.html

import argparse
import csv
import json
import sys

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
        self.assigned_ipv4_subnets = []
        self.assigned_ipv6_subnets = []

    def get_all_tags(self, key:str):
        return [x["Value"] for x in self.tags if x["Key"] == key]

    def get_tag(self, key:str):
        value = None
        values = self.get_all_tags(key)
        if values:
            value = values[0]
        return value

    def contains_subnet(self, subnet:str):
        # IPv4
        subnet_count = len([x for x in self.assigned_ipv4_subnets if x["CidrBlock"] == subnet])
        # IPv6
        subnet_count += len([x for x in self.assigned_ipv6_subnets if x["Ipv6CidrBlock"] == subnet])
        return subnet_count > 0

class SecurityGroupPrinter(object):
    def print_csv(self, security_groups:list, vpcs=[]):
        output = []
        for security_group in security_groups:
            for permission in security_group.ip_permissions:
                output_dict = {}
                # get the current vpc (if it exists in the vpc list provided)
                cur_vpc = [x for x in vpcs if security_group.vpc_id == x.vpc_id]
                # we should only have 1 vpc
                if len(cur_vpc) == 1:
                    cur_vpc = cur_vpc[0]
                elif len(cur_vpc) > 1:
                    raise Exception("Found more than one VPC with the same ID")
                # continue
                output_dict["vpc_id"] = security_group.vpc_id
                if cur_vpc:
                    output_dict["vpc_id"] = output_dict["vpc_id"] + " (" + str(cur_vpc.get_tag("Name")) + ")"
                output_dict["group_id"] = security_group.group_id + " (" + str(security_group.name) + ")"
                output_dict["tags"] = ",".join([str(x["Key"] + "=" + x["Value"]) for x in security_group.tags])
                output_dict["direction"] = permission.direction
                # build from/to field
                output_ranges = []
                output_ranges += [str(x["CidrIp"]) for x in permission.ipv4_ranges]
                output_ranges += [str(x["CidrIp6"]) for x in permission.ipv6_ranges]
                output_ranges += [str(x["PrefixListId"]) for x in permission.prefix_list_ids]
                output_ranges += [str(x["UserId"] + "/" + x["GroupId"]) for x in permission.user_id_group_pairs]
                output_dict["permitted_entity"] = ",".join([str(x) for x in output_ranges])
                # set the ports to a single field
                if permission.from_port == permission.to_port:
                    output_dict["port_no"] = permission.from_port
                else:
                    output_dict["port_no"] = str(permission.from_port) + "-" + str(permission.to_port)
                # set the protocol to a readable format
                if permission.protocol == "-1":
                    output_dict["protocol"] = "any"
                else:
                    output_dict["protocol"] = permission.protocol
                output.append(output_dict)
        # if we have no ouput abandon
        if not output:
            return None
        # write the csv output
        writer = csv.DictWriter(sys.stdout, fieldnames=output[0].keys())
        writer.writeheader()
        writer.writerows(output)
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
            cur_vpc.assigned_ipv4_subnets = vpc.get("CidrBlockAssociationSet",[])
            cur_vpc.assigned_ipv4_subnets = vpc.get("Ipv6CidrBlockAssociationSet",[])
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
    parser.add_argument("--groups", help="Path to file containing ec2 describe-security-groups")
    parser.add_argument("--vpcs", help="Path to file containing ec2 describe-vpcs")
    parser.add_argument("--instances", help="Path to file containing ec2 describe-instances")
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
