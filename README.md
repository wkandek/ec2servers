# ec2servers

ec2servers.py retriesves the EC2 instance data from the accounts listed and processes the data. Can be done adhoc or periodically.
Account data gets stored and accessed in pickle files to allow for quicker iteration when modifying the script. 

Production runs are typiclaly with options --remote and --record to actually use the AWS API instead

I have used it to plot costs data in New Relic:
- loop over all production accounts
- look up the cost of the instance type in a CSV
- uploa the cost ot New Relic as a metric for each account

I have also used it to analyze progress in migration instances from intel to intel next generation or amd to graviton 
