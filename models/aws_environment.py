class AWSEnvironment(object):
    def __init__(self):
        self.instances = []
        self.security_groups = []
        self.subnets = []
        self.vpcs = []

    def get_vpc_by_id(self, id:str):
        return [x for x in self.vpcs if x.vpc_id == id]

    def get_security_group_by_id(self, id:str):
        return [x for x in self.security_groups if x.group_id == id]

    def get_subnet_by_id(self, id:str):
        return [x for x in self.subnets if x.subnet_id == id]

    def get_instance_by_id(self, id:str):
        return [x for x in self.instances if x.instance_id == id]

    def get_subnet_by_cidr(self, cidr:str):
        return [x for x in self.subnets if x.cidr == cidr]

    def get_instances_with_security_group(self, security_group_id):
        return [x for x in self.instances if x.has_security_group(security_group_id)]