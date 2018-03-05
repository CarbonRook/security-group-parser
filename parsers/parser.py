import json

class AWSParser(object):
    def __init__(self, in_json:str):
        self.json = json.loads(in_json)

    def parse(self):
        raise NotImplementedError("Parse function not implemented")

    def get_tag_dict(self, tags:list):
        tag_dict = {}
        for tag in tags:
            tag_dict[tag["Key"]] = tag["Value"]
        return tag_dict
