import boto3
from keys import awsid, awskey, awsregion
import pickle
import argparse
import os
import csv
import time
  
# ts stores the time in seconds
ts = time.time()
  

def analyzeInstances(account, id, key, region, cost):

  ec2_client = boto3.client("ec2", region_name = region,
  #ec2_client = boto3.client("ec2", 
                             aws_access_key_id = id,
                             aws_secret_access_key = key)

  # use API or local file
  if args.remote:
    reservations = ec2_client.describe_instances(Filters=[
      {
        "Name": "instance-state-name",
        "Values": ["running"],
      }]
    ).get("Reservations")
  else:
    if os.path.exists(account+".pickle"):
      with open(account+".pickle", 'rb') as handle:
        reservations = pickle.load(handle)
    else:
      reservations = {}

  # record newlocal file
  if args.record:
    with open(account+".pickle", "wb") as handle:
      pickle.dump(reservations, handle, protocol=pickle.HIGHEST_PROTOCOL)

  # figure out cost per cluster element
  total_cost = 0
  unallocated_cost = 0
  sum = {}
  count = {}
  for reservation in reservations:
    clusterelement = "N/A"
    for instance in reservation["Instances"]:
      instance_id = instance["InstanceId"]
      instance_type = instance["InstanceType"]
      print(instance_type)
      name = instance["Tags"]
      if "PublicIpAddress" in instance:
        publicip = instance["PublicIpAddress"]
      else:
        publicip = "n/a"
      ip = instance["PrivateIpAddress"]

      instancecost = "N/A"
      if instance_type in cost:
        instance_cost = cost[instance_type]
        total_cost = total_cost + instance_cost

      # find the cluster name
      for (kv) in name:
        if "Cluster" in kv["Key"] or "aws:eks:cluster-name" in kv["Key"] or "opsworks:stack" in kv["Key"]:
          clusterelement = kv["Value"]
          print("NF",kv["Key"],kv["Value"], instance_id, instance_type)
        else:
          print(kv["Key"],kv["Value"], instance_id, instance_type)
      print("IPs=", publicip, ip)
      print("CE=",clusterelement)
      if "N/A" in clusterelement:
        # keep track of cost not allocated 
        unallocated_cost = unallocated_cost + instance_cost

      if clusterelement in count:
        count[clusterelement] = count[clusterelement] + 1 
      else:
        count[clusterelement] = 1 

      if clusterelement in sum:
        sum[clusterelement] = sum[clusterelement] + instance_cost
      else:
        sum[clusterelement] = instance_cost
      print(f"{account} {instance_id}, {instance_type} {clusterelement} {instance_cost} {total_cost} {unallocated_cost}" )

  return len(reservations), sum, count


# main
# build commandline options and defaults - default = remote = false, record = false, details = false
parser = argparse.ArgumentParser(description='Just True and False')
parser.add_argument('--debug', dest="debug", default=False, action="store_true", help="debug")
parser.add_argument('--remote', dest="remote", default=False, action="store_true", help="use API or local files")
parser.add_argument('--record', dest="record", default=False, action="store_true", help="record APIs to local files")
args = parser.parse_args()

# load the costs of the servers from a CSV
servercost = {}
with open("ec2servers.csv", newline="") as csvfile:
  csvcost = csv.DictReader(csvfile, delimiter=',', quotechar='"')
  for row in csvcost:
    servercost[row["ServerType"]] = int(row["ServerCost"])

# check installations - awsid, etc comes from keys.py
prod = {}
account = "prod"
if True:
#for account in ("prod"):
  (instances,prod,servers) = analyzeInstances(account, awsid[account], awskey[account], awsregion[account], servercost)

  # print results
  print(f"Prod:{ts}:{instances}&", end="")
  i = 0
  for k in servers:
    print(f"{k}={servers[k]}", end ="")
    i = i + 1
    if i < len(prod):
      print("&", end = "")

  i = 0
  for k in prod:
    print(f"{k}={prod[k]}", end ="")
    i = i + 1
    #if i < len(edpprod):
    #  print("&", end = "")
    #else:
    #  print()
    print()

