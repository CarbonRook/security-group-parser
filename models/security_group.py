class SecurityGroup(object):
    def __init__(self):
        self.description = ""
        self.name = ""
        self.owner_id = ""
        self.group_id = ""
        self.tags = []
        self.vpc_id = ""
        self.ip_permissions = []

