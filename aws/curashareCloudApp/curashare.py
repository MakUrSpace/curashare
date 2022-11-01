from dataclasses import dataclass, asdict
import json
import markdown
from curashareCloudApp.murd import murd, mddb


@dataclass
class CuraProfile:
    groupName = "CuraProfile"
    Id: str
    CuraData: str
    CuraSettings: dict

    def __repr__(self):
        return json.dumps(asdict(self), indent=4)

    @classmethod
    def fromm(cls, m):
        kwargs = {k: v for k, v in m.items() if k in cls.__dataclass_fields__.keys()}
        kwargs['CuraSettings'] = cls.parseSettings(kwargs['CuraData'].replace('\r\n', '\n'))
        return cls(**kwargs)

    def asm(self):
        curaProfileMurd = {
            mddb.group_key: self.groupName,
            mddb.sort_key: self.Id,
            **asdict(self)}
        curaProfileMurd.pop('CuraSettings')
        return curaProfileMurd

    def set(self):
        murd.update([self.asm()])

    def __repr__(self):
        metadata = self.CuraSettings['0']['general']
        profileName = metadata['Profile']
        quality = metadata['Quality']
        profileDate = metadata['Date']
        return f"{quality}-{profileName}-asOf-{profileDate}"

    class UnrecognizedObject(Exception):
        """ Exception for failing to recover a object definition """

    @classmethod
    def retrieve(cls, CuraProfileId=None):
        try:
            if CuraProfileId is None:
                return [cls.fromm(p) for p in murd.read(group=cls.groupName)]
            else:
                return cls.fromm(murd.read_first(group=cls.groupName, sort=CuraProfileId))
        except Exception:
            raise cls.UnrecognizedObject(f"Unable to locate CuraProfile {CuraProfileId}")

    @staticmethod
    def parseSettings(settingString):
        settings = {}
        for setting in settingString.split('\n')[1:-1]:
            group, extruder, key, valueType, value = setting.split(';')
            if extruder not in settings:
                settings[extruder] = {}
            if group not in settings[extruder]:
                settings[extruder][group] = {}
            settings[extruder][group][key] = value
        return settings


def curaProfileToMarkdown(curaProfile: CuraProfile):
    content = ""
    groupHeader = """
### {groupName}
"""
    groupItemTemplate = """
    * {itemName:60} || {itemValue}
"""

    content += f"""
# {curaProfile} Configuration
"""

    for extruderNumber in range(1, int(curaProfile.CuraSettings['0']['general']['Extruder_Count']) + 1):
        extruderConfig = curaProfile.CuraSettings[str(extruderNumber)]
        content += f"""
## Extruder {extruderNumber} Config
"""
        for group, groupConfig in extruderConfig.items():
            content += groupHeader.format(groupName=group)
            for itemName, itemValue in groupConfig.items():
                content += groupItemTemplate.format(itemName=itemName, itemValue=itemValue)

    return content


def markdownToHtml(markdownContent):
    return markdown.markdown(markdownContent, output_format="html5")


def build_Lambda_response(status_code=200, body="", headers={}):
    return {
        "statusCode": status_code,
        "headers": headers,
        "body": body
    }


def post_Profile(event):
    profileId = event.get("pathParameters", {}).get("profile_id")
    if profileId is None:
        return build_Lambda_response(status_code=403)
    data = event.get("body")
    curaProfile = CuraProfile(Id=profileId, CuraData=data)
    curaProfile.set()
    return build_Lambda_response(body="Profile posted")


def get_Profile(event):
    curaProfileId = event.get("pathParameters", {}).get("profile_id")
    if curaProfileId is None:
        return build_Lambda_response(status_code=404)
    curaProfile = CuraProfile.retrieve(curaProfileId)
    profilePage = markdownToHtml(curaProfileToMarkdown(curaProfile))
    return build_Lambda_response(body=profilePage, headers={"content-type": "text/html"})


def Lambda_handler(event, context):
    print(event)
    method = str(event.get("httpMethod")).lower()
    if method == "get":
        return get_Profile(event)
    elif method == "post":
        return post_Profile(event)
    else:
        return build_Lambda_response(400)
