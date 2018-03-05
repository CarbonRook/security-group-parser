import csv
import sys


class CSVPrinter(object):
    def print_csv(self, security_groups: list, vpcs=None, instances=None, subnets=None):
        output = []
        for security_group in security_groups:
            # Affected instances are the instances which have the security assigned to them
            instances_affected = []
            if instances is not None:
                # If we have been given instance desciption then we can retrieve a list of affected instances
                instances_affected = []
                for instance in instances:
                    if instance.has_security_group(security_group.group_id):
                        instances_affected.append(CSVPrinter.get_enriched_str(instance.id, instance.get_tag("Name")))
            for permission in security_group.ip_permissions:
                output_dict = dict()
                # Get the VPC ID and the associated VPC name from the Name tag is available
                output_dict["vpc_id"] = CSVPrinter.enrich_vpc(security_group, vpcs)
                # Get the security group ID and group name
                output_dict["group_id"] = CSVPrinter.get_enriched_str(security_group.group_id, str(security_group.name))
                # Get a "Key1=Value1,Key2=Value2" string from all tags defined in the security group
                output_dict["tags"] = CSVPrinter.get_name_value_pair_string(security_group.tags)
                # Get the direction of the rule "ingress" or "egress"
                output_dict["direction"] = permission.direction
                # build the list of entities that the rule permits access to/from
                output_dict["permitted_entity"] = CSVPrinter.enrich_all_permitted_entities(permission, subnets)
                # set the ports to a single field "first-last", map the "-1" port to "any"
                output_dict["port_no"] = self.map_variable(self.cat_ports(permission.from_port, permission.to_port))
                # set the protocol to a readable format (-1 is used to mean any so print "any")
                output_dict["protocol"] = self.map_variable(permission.protocol)
                # Set the affected instances defined earlier for this security group
                output_dict["affected_instances"] = ", ".join(instances_affected)
                output.append(output_dict)
        # if we have no ouput abandon
        if not output:
            return None
        # write the csv output
        writer = csv.DictWriter(sys.stdout, fieldnames=output[0].keys())
        writer.writeheader()
        writer.writerows(output)
        return None

    @staticmethod
    def get_name_value_pair_string(tags: dict):
        return ",".join([x + "=" + y for x, y in tags.items()])

    @staticmethod
    def get_enriched_str(x: str, y: str):
        return x + " (" + y + ")"

    @staticmethod
    def enrich_vpc(self, security_group, vpcs):
        # Check if we have VPCs defined
        if not vpcs:
            return security_group.vpc_id

        enriched_vpcs = []
        # get the current vpc (if it exists in the vpc list provided)
        vpcs_with_id = [x for x in vpcs if x.vpc_id == security_group.vpc_id]
        if len(vpcs_with_id) > 0:
            vpcs_names_arr = []
            for vpc in vpcs:
                vpcs_names_arr.append(vpc.get_tag("Name"))
            vpc_names = ",".join(vpcs_names_arr)
            enriched_vpcs.append(CSVPrinter.get_enriched_str(security_group.vpc_id, vpc_names))
        else:
            enriched_vpcs.append(security_group.vpc_id)
        return enriched_vpcs

    @staticmethod
    def enrich_subnets(unenriched_ipv4_cidrs, subnets):
        # We only have CIDR but we want CIDR and the name associated with the CIDR if possible
        enriched_ipv4_ranges = []
        for cidr in unenriched_ipv4_cidrs:
            subnets = [x for x in subnets if x.cidr == cidr]
            if len(subnets) > 0:
                subnet_names_arr = []
                for subnet in subnets:
                    subnet_names.append(subnet.get_tag("Name"))
                subnet_names = ",".join(subnet_names_arr)
                enriched_ipv4_ranges.append(cidr + " (" + subnet_names + ")")
            else:
                enriched_ipv4_ranges.append(cidr)
        return enriched_ipv4_ranges

    @staticmethod
    def enrich_all_permitted_entities(permission, subnets):
        unenriched_ipv4_ranges = [str(x["CidrIp"]) for x in permission.ipv4_ranges]
        unenriched_ipv6_ranges = [str(x["CidrIp6"]) for x in permission.ipv6_ranges]

        output_ranges = []
        if subnets:
            output_ranges += CSVPrinter.enrich_subnets(unenriched_ipv4_ranges, subnets)
        else:
            output_ranges += unenriched_ipv4_ranges

        # TODO: Enrich ipv6
        output_ranges += unenriched_ipv6_ranges
        output_ranges += [str(x["PrefixListId"]) for x in permission.prefix_list_ids]
        output_ranges += [str(x["UserId"] + "/" + x["GroupId"]) for x in permission.user_id_group_pairs]
        return ",".join(output_ranges)

    @staticmethod
    def map_variable(input_str):
        var_map = {
                "0.0.0.0/0": "any",
                "-1": "any"
                }
        if input_str in var_map:
            return var_map[input_str]
        else:
            return input_str

    @staticmethod
    def cat_ports(from_port, to_port):
        if from_port == to_port:
            return str(from_port)
        return str(from_port) + "-" + str(to_port)

