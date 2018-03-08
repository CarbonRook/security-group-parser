class DBInstance(object):
    def __init__(self):
        self.db_instance_id = ""
        self.db_instance_resource_id = ""
        self.db_instance_port = ""
        self.db_engine_version = ""
        self.db_is_encrypted = ""
        self.endpoint = {} # dict of port and address
        self.db_name = ""
        self.db_subnet_group = {} 
        self.vpc_security_groups = []
        self.db_is_publicly_accessible = ""

    def has_security_group(self, security_group_id):
        sg_ids = [x for x in self.vpc_security_groups if x["VpcSecurityGroupId"] == security_group_id]
        return len(sg_ids) > 0
