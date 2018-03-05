class Instance(object):
    def __init__(self):
        self.vpc_id = ""
        self.instance_id = ""
        self.image_id = ""
        self.private_dns_name = ""
        self.public_dns_name = ""
        self.private_ip_address = ""
        self.security_groups = [] # dict of GroupName and GroupId
        self.tags = []
        self.interfaces = []
        self.owner_id = ""
        self.reservation_id = ""

    def has_security_group(self, security_group_id):
        sg_ids = [x for x in self.security_groups if x["GroupId"] == security_group_id]
        return len(sg_ids) > 0

    def get_tag(self, tag_name):
        return self.tags.get(tag_name, None)