#!/bin/bash

cd instance_deployment

python deploy_instance.py

# check running instance and write public ip to public_ip.txt
python check_running_instance.py

# read the public ip from public_ip.txt and do work
while IFS='' read -r public_ip || [[ -n "$public_ip" ]]
do
    echo "Public IP: $public_ip"
    # copy the code to the instance
    scp -i waldoge_key_pair.pem -r copy_to_aws/lab1_code ubuntu@${public_ip}:~/
    scp -i waldoge_key_pair.pem copy_to_aws/setup_lab1.sh ubuntu@${public_ip}:~/

    # setup environment and run the page on aws
    ssh -i waldoge_key_pair.pem ubuntu@${public_ip} 'source setup_lab1.sh'
done < "public_ip.txt"

cd ..