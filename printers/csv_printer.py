import csv
import sys

class CSVPrinter(object):
    def print_csv(self, security_groups:list, vpcs=None, instances=None, subnets=None):
        output = []
        for security_group in security_groups:
            instances_affected = []
            if instances:
                instances_affected = [x.instance_id + " (" + x.get_tag("Name") + ")" for x in instances if x.has_security_group(security_group.group_id)]
            for permission in security_group.ip_permissions:
                output_dict = {}
                
                # Check if we have VPCs defined
                if vpcs is not None:
                    # get the current vpc (if it exists in the vpc list provided)
                    cur_vpc = [x for x in vpcs if security_group.vpc_id == x.vpc_id]
                    # get the first element or, if not found, set None
                    cur_vpc = next(iter(cur_vpc), None)
                else:
                    cur_vpc = None

                # continue
                output_dict["vpc_id"] = security_group.vpc_id
                if cur_vpc:
                    output_dict["vpc_id"] = output_dict["vpc_id"] + " (" + str(cur_vpc.get_tag("Name")) + ")"
                output_dict["group_id"] = security_group.group_id + " (" + str(security_group.name) + ")"
                output_dict["tags"] = ",".join([x + "=" + y for x,y in security_group.tags.items()])
                output_dict["direction"] = permission.direction
                # build from/to field
                output_dict["permitted_entity"] = ", ".join([str(x) for x in self.build_permitted_range_list(permission, subnets)])
                # set the ports to a single field
                output_dict["port_no"] = self.map_variable(self.cat_ports(permission.from_port, permission.to_port))
                # set the protocol to a readable format
                output_dict["protocol"] = self.map_variable(permission.protocol)
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

    def enrich_subnets(self, unenriched_ipv4_cidrs, subnets):
        # We want CIDR and the subnet name if possible
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


    def build_permitted_range_list(self, permission, subnets):
        # Grab the unenriched ranges
        unenriched_ipv4_ranges = [str(x["CidrIp"]) for x in permission.ipv4_ranges]
        unenriched_ipv6_ranges = [str(x["CidrIp6"]) for x in permission.ipv6_ranges]

        output_ranges = []
        if subnets:
            output_ranges += self.enrich_subnets(unenriched_ipv4_ranges, subnets)
        else:
            output_ranges += unenriched_ipv4_ranges

        # TODO: Enrich ipv6
        output_ranges += unenriched_ipv6_ranges
        output_ranges += [str(x["PrefixListId"]) for x in permission.prefix_list_ids]
        output_ranges += [str(x["UserId"] + "/" + x["GroupId"]) for x in permission.user_id_group_pairs]
        return output_ranges
        

    def map_variable(self, input_str):
        var_map = {
                "0.0.0.0/0": "any",
                "-1": "any"
                }
        if input_str in var_map:
            return var_map[input_str]
        else:
            return input_str

    def cat_ports(self, from_port, to_port):
        if from_port == to_port:
            return str(from_port)
        return str(from_port) + "-" + str(to_port)

