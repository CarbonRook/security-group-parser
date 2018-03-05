import json
from parsers.aws_parser import AWSParser
from models.vpc import VPC

class VPCParser(AWSParser):
        
    def parse(self):
        parsed_vpcs = []
        for vpc in self.json["Vpcs"]:
            cur_vpc = VPC()
            cur_vpc.vpc_id = vpc["VpcId"]
            cur_vpc.tags = self.get_tag_dict(vpc.get("Tags",[]))
            cur_vpc.state = vpc["State"]
            cur_vpc.is_default = vpc["IsDefault"]
            cur_vpc.cidr = vpc["CidrBlock"]
            cur_vpc.assigned_ipv4_subnets = vpc.get("CidrBlockAssociationSet",[])
            cur_vpc.assigned_ipv4_subnets = vpc.get("Ipv6CidrBlockAssociationSet",[])
            parsed_vpcs.append(cur_vpc)
        return parsed_vpcs

