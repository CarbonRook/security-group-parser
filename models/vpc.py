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

