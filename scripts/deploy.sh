#!/bin/bash
cdk deploy --outputs-file config.json
python3 ./iac/post_deploy.py