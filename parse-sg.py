#!/usr/bin/env python3

# Reference https://docs.aws.amazon.com/cli/latest/reference/ec2/describe-security-groups.html

import argparse
from parsers.security_group_parser import SecurityGroupParser
from parsers.vpc_parser import VPCParser
from parsers.instance_parser import InstanceParser
from printers.csv_printer import CSVPrinter

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
    parsed_sgs = sg_parser.parse()

    parsed_vpcs = None
    if args.vpcs:
        with open(args.vpcs, 'r') as describe_vpc_file:
            vpc_description = describe_vpc_file.read()
        vpc_parser = VPCParser(vpc_description)
        parsed_vpcs = vpc_parser.parse()

    parsed_instances = None
    if args.instances:
        with open(args.instances, 'r') as describe_instances_file:
            instance_description = describe_instances_file.read()
        instance_parser = InstanceParser(instance_description)
        parsed_instances = instance_parser.parse()

    sg_printer = CSVPrinter().print_csv(parsed_sgs, parsed_vpcs, parsed_instances)
 
    return 0


if __name__ == "__main__":
    main()
