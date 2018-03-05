class Subnet(object):
    def __init__(self):
        self.vpc_id = ""
        self.subnet_id = ""
        self.available_ip_address_count = ""
        self.state = ""
        self.availability_zone = ""
        self.cidr = ""
        self.tags = []

    def get_tag(self, tag_name):
        return self.tags.get(tag_name, None)
