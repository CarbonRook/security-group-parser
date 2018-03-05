import json
from models.vpc import VPC

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

