import csv
import sys

class CSVPrinter(object):
    def print_csv(self, security_groups:list, vpcs=None, instances=None):
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
                output_ranges = []
                output_ranges += [str(x["CidrIp"]) for x in permission.ipv4_ranges]
                output_ranges += [str(x["CidrIp6"]) for x in permission.ipv6_ranges]
                output_ranges += [str(x["PrefixListId"]) for x in permission.prefix_list_ids]
                output_ranges += [str(x["UserId"] + "/" + x["GroupId"]) for x in permission.user_id_group_pairs]
                output_dict["permitted_entity"] = ",".join([str(x) for x in output_ranges])
                # set the ports to a single field
                output_dict["port_no"] = self.cat_ports(permission.from_port, permission.to_port)
                # set the protocol to a readable format
                output_dict["protocol"] = self.map_variable(permission.protocol)
                output_dict["affected_instances"] = ",".join(instances_affected)
                output.append(output_dict)
        # if we have no ouput abandon
        if not output:
            return None
        # write the csv output
        writer = csv.DictWriter(sys.stdout, fieldnames=output[0].keys())
        writer.writeheader()
        writer.writerows(output)
        return None

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

