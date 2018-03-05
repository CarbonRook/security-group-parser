import json
from parsers.parser import AWSParser
from models.subnet import Subnet

class SubnetParser(AWSParser):
        
    def parse(self):
        parsed_subnets = []
        for subnet in self.json["Subnets"]:
            cur_subnet = Subnet()
            cur_subnet.subnet_id = subnet["SubnetId"]
            cur_subnet.vpc_id = subnet["VpcId"]
            cur_subnet.availability_zone = subnet["AvailabilityZone"]
            cur_subnet.available_ip_address_count = subnet["AvailableIpAddressCount"]
            cur_subnet.cidr = subnet["CidrBlock"]
            cur_subnet.state = subnet["State"]
            cur_subnet.tags = self.get_tag_dict(subnet.get("Tags",[]))
            parsed_subnets.append(cur_subnet)
        return parsed_subnets

