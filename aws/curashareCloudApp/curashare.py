from dataclasses import dataclass, asdict
import json
from curashareCloudApp.murd import murd, mddb


@dataclass
class CuraProfile:
    groupName = "CuraProfile"
    Id: str
    CuraData: str

    def __repr__(self):
        return json.dumps(asdict(self), indent=4)

    @classmethod
    def fromm(cls, m):
        kwargs = {k: v for k, v in m.items() if k in cls.__dataclass_fields__.keys()}
        return cls(**kwargs)

    def asm(self):
        return {mddb.group_key: self.groupName,
                mddb.sort_key: self.Id,
                **asdict(self)}

    def set(self):
        murd.update([self.asm()])

    class UnrecognizedObject(Exception):
        """ Exception for failing to recover a object definition """

    @classmethod
    def retrieve(cls, CuraProfileId):
        try:
            return cls.fromm(murd.read_first(group=cls.groupName, sort=CuraProfileId))
        except Exception:
            raise cls.UnrecognizedObject(f"Unable to locate CuraProfile {CuraProfileId}")


def build_Lambda_response(status_code=200, body="", headers={}):
    return {
        "statusCode": status_code,
        "headers": headers,
        "body": body
    }


def post_Profile(event):
    profileId = event.get("pathParameters", {}).get("profile_id")
    data = event.get("body")
    curaProfile = CuraProfile(Id=profileId, CuraData=data)
    curaProfile.set()
    return build_Lambda_response(body="Profile posted")


def get_Profile(event):
    curaProfileId = event.get("profile_id", "")
    curaProfile = CuraProfile.retrieve(curaProfileId)
    return build_Lambda_response(body=json.dumps(curaProfile))


def Lambda_handler(event, context):
    print(event)
    method = str(event.get("httpMethod")).lower()
    if method == "get":
        return get_Profile(event)
    elif method == "post":
        return post_Profile(event)
    else:
        return build_Lambda_response(400)
