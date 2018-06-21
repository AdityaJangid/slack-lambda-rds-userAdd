#==================================================================================================
# This python script is used to add user and reset password of rds instance using a slack command
#==================================================================================================

import sys
import boto3
import logging
import pymysql
import os
import cgi
from base64 import b64decode
dbs = {'info':'command-test.cj8hufhw12ic.us-east-1.rds.amazonaws.com', 'restricted':'command-test2.cj8hufhw12ic.us-east-1.rds.amazonaws.com'}

##### uncomment the following lines to take encrypted environmental variables from lambda function
#  enc_admin_name           =    os.environ["admin_name"]
#  admin_name_inbyte        =    boto3.client('kms').decrypt(CiphertextBlob=b64decode(enc_admin_name))['Plaintext']
#  admin_name               =    admin_name_inbyte.decode("utf-8")
#
#  enc_admin_password       =    os.environ["admin_password"]
#  admin_password_inbyte    =    boto3.client('kms').decrypt(CiphertextBlob=b64decode(enc_admin_password))['Plaintext']
#  admin_password           =    admin_password_inbyte.decode("utf-8")
#

##### Hard coded values for admin user and password
admin_name               =    "aditya"
admin_password           =    "aditya123"
db_name                  =    "slack"
prcnt                    =    "%"

logger = logging.getLogger()
logger.setLevel(logging.INFO)

#### Function to create a user in mysql rds instance. Only admin user can run this
def create_user(info):
    rds_instance,username,password,permission = info.split()
    rds_host = dbs[rds_instance]
    try:
       conn = pymysql.connect(rds_host, user=admin_name, passwd=admin_password, db=db_name, connect_timeout=10)
    except:
       logger.error("ERROR: Unexpected error: Could not connect to MySql instance.")
       sys.exit()
    with conn.cursor() as cur:
       cur.execute("CREATE USER '%s'@'%s' IDENTIFIED BY '%s'" % (username,prcnt,password))
       cur.execute("grant %s on slack.* to %s@'%s'" %(permission,username,prcnt))
       cur.execute("commit")
       cur.execute("flush privileges")
       conn.commit()
    return ("user %s added successfully" % (username))

##### Function to reset the password when you know your old password. Every user will be able to run this
def reset_password(info):
    rds_instance,username,old_password,new_password = info.split()
    rds_host = dbs[rds_instance]
    try:
       conn = pymysql.connect(rds_host, user=username, passwd=old_password, db=db_name, connect_timeout=10)
    except:
       logger.error("ERROR: Unexpected error: Could not connect to MySql instance.")
       sys.exit()
    with conn.cursor() as cur:
       cur.execute("SET PASSWORD = PASSWORD('%s')"%(new_password))
       conn.commit()
    return ("password of user %s changed successfully" % (username))

##### Function to reset the password when you forgot your old password. Only admin user will be able to run this
def reset_password_by_admin(info):
    db_name = "mysql"
    rds_instance,username,new_password = info.split()
    rds_host = dbs[rds_instance]
    try:
       conn = pymysql.connect(rds_host, user=admin_name, passwd=admin_password, db=db_name, connect_timeout=10)
    except:
       logger.error("ERROR: Unexpected error: Could not connect to MySql instance.")
       sys.exit()
    with conn.cursor() as cur:
        cur.execute("update user set password=PASSWORD('%s') where User='%s'"%(new_password, username))
        cur.execute("FLUSH PRIVILEGES")
        conn.commit()
    return ("password of user %s changed successfully" % (username))

def handler(event, context):
    pass
    params = cgi.parse_qs(event['body'])
    command,info = params['text'][0].split(" ", 1)
    invoked_by = params['user_name'][0]

    if command == "reset_password":
        if invoked_by == "aditya.jangid":
            reset_password_by_admin(info)
        else:
            reset_password(info)

    if command=="create_user" and invoked_by == "aditya.jangid":
        create_user(info)
    else:
        return "ERROR: you have not proper permission to create a user"
