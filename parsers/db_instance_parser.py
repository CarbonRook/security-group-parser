import json
from parsers.aws_parser import AWSParser
from models.db_instance import DBInstance
from models.subnet import Subnet

class DBInstanceParser(AWSParser):
        
    def parse(self):
        parsed_instances = []
        for instance in self.json["DBInstances"]:
            cur_instance = DBInstance()
            cur_instance.db_instance_id = instance["DBInstanceIdentifier"]
            cur_instance.db_instance_resource_id = instance["DbiResourceId"]
            cur_instance.db_instance_port = instance["DbInstancePort"]
            cur_instance.db_engine_version = instance["EngineVersion"]
            cur_instance.db_is_encrypted = instance["StorageEncrypted"]
            cur_instance.endpoint = instance["Endpoint"]
            cur_instance.db_name = instance["DBName"]
            cur_instance.db_subnets = instance["DBSubnetGroup"]
            cur_instance.vpc_security_groups = instance["VpcSecurityGroups"]
            cur_instance.db_is_publicly_accessible = instance["PubliclyAccessible"]
            parsed_instances.append(cur_instance)
        return parsed_instances

