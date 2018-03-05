class IPPermission(object):
    def __init__(self):
        self.direction = "" # ingress/egress
        self.from_port = None
        self.to_port = None
        self.protocol = ""
        self.ipv4_ranges = [] # dict of CidrIp and Description
        self.ipv6_ranges = [] # dict of CidrIp6 and Description
        self.prefix_list_ids = [] # dict of PrefixListId and Description
        self.user_id_group_pairs = [] # dict of GroupId, GroupName, UserId, Description, PeeringStatus, VpcId, VpcPeeringConnectionId

