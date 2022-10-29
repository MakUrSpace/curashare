from time import sleep

from murdaws import murd_ddb as mddb


murd = None


try:
    mddb.ddb_murd_prefix = "curashare_"
    murd = mddb.DDBMurd("profiles")
except Exception:
    print("Unable to locate CuraShare DynamoDB table. Use provision_CuraShare_tables to build them")


def provision_CuraShare_tables():
    global murd
    mddb.DDBMurd.create_murd_table("profiles")
    sleep(10)
    murd = mddb.DDBMurd("profiles")
    return murd
