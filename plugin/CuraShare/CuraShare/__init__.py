# Copyright (c) 2022 5@xes
# ImportExportProfiles is released under the terms of the AGPLv3 or higher.

from . import CuraShare

def getMetaData():
    return {}

def register(app):
    return {"extension": CuraShare.CuraShare()}
