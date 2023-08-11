import boto3
from keys import awsid, awskey, awsregion
import pickle
import argparse
import os
  

def print_event(event, status, names):
  if args.all or "[completed]" not in event["Description"].lower():
    print("Event:", event["Code"])
    print(" ", names[status["InstanceId"]], status["InstanceId"], "in AZ", status["AvailabilityZone"])
    print(" ", event["Description"])
    print(" ", event["NotAfter"])
    print(" ", event["NotBefore"])


def analyzeInstances(id, key, region):

  ec2_client = boto3.client("ec2", region_name = region,
                             aws_access_key_id = id,
                             aws_secret_access_key = key)
  reservations = ec2_client.describe_instances(Filters=[
      {
        "Name": "instance-state-name",
        "Values": ["running"],
      }]
    ).get("Reservations")

  # for each host get detailed status - in chunks of 100
  # build the while list
  instanceids = []
  names = {} 
  for reservation in reservations:
    for instance in reservation["Instances"]:
      instance_id = instance["InstanceId"]
      instanceids.append(instance_id)
      tags = instance["Tags"]
      instancename = "n/a"
      for tag in tags:
        if tag["Key"] == "Name":
          instancename = tag["Value"]
          names[instance_id] = instancename

  # chunk it - AWS API requires it
  l = len(instanceids) 
  inc = 99
  start = 0
  end = start + inc

  while end < l:
    shortlist = instanceids[start:end]
    detailedstatus = ec2_client.describe_instance_status(InstanceIds=shortlist)
    for status in detailedstatus['InstanceStatuses']:
      if "Events" in status:
        for event in status["Events"]:
          print_event(event, status, names)
    start = end + 1
    end = start + inc
  shortlist = instanceids[start:l-1]
  detailedstatus = ec2_client.describe_instance_status(InstanceIds=shortlist)
  for status in detailedstatus['InstanceStatuses']:
    if "Events" in status:
      for event in status["Events"]:
        print_event(event, status, names)


# main
# build commandline options and defaults - default = remote = false, record = false, details = false
parser = argparse.ArgumentParser(description='Just True and False')
parser.add_argument('--all', dest="all", default=False, action="store_true", help="print also completed events")
args = parser.parse_args()

# check installations - awsid, etc comes from keys.py
account = "prod"
analyzeInstances(awsid[account], awskey[account], awsregion[account])
