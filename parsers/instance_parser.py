import json
from parsers.parser import AWSParser
from models.instance import Instance

class InstanceParser(AWSParser):
        
    def parse(self):
        parsed_instances = []
        # A reservation is the act of launching instances
        # The instances within are the instances that were spun up
        # So, the reservation owner ID is the account which spun up the instances
        # Because you can spin up multiple instances at once, you can have multiple instances within a reservation
        for reservation in self.json["Reservations"]:
            for instance in reservation["Instances"]:
                cur_instance = Instance()
                cur_instance.instance_id = instance["InstanceId"]
                cur_instance.vpc_id = instance["VpcId"]
                cur_instance.image_id = instance["ImageId"]
                cur_instance.public_dns_name = instance["PublicDnsName"]
                cur_instance.private_dns_name = instance["PrivateDnsName"]
                cur_instance.private_ip_address = instance["PrivateIpAddress"]
                cur_instance.security_groups = instance.get("SecurityGroups", [])
                cur_instance.tags = self.get_tag_dict(instance.get("Tags",[]))
                cur_instance.interfaces = instance.get("Interfaces", [])
                cur_instance.owner_id = reservation.get("OwnerId", None)
                cur_instance.reservation_id = reservation.get("ReservationId", None)
                parsed_instances.append(cur_instance)
        return parsed_instances

