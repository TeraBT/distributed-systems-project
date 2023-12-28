#!/usr/bin/env bash

db_table_name=central_table
aws dynamodb create-table \
  --table-name $db_table_name \
  --attribute-definitions \
    AttributeName=PK,AttributeType=S \
    AttributeName=SK,AttributeType=S \
  --key-schema \
    AttributeName=PK,KeyType=HASH \
    AttributeName=SK,KeyType=RANGE \
  --billing-mode PAY_PER_REQUEST \
  --no-deletion-protection-enabled

bucket_name="central-bucket"$(uuidgen)
aws s3api create-bucket \
    --bucket $bucket_name

lambda_runtime=python3.11
lab_role=$(
aws iam get-role \
    --role-name LabRole \
    --query 'Role.Arn' \
    --output text
)

create_lambda () {
    aws lambda create-function \
        --function-name $1 \
        --runtime $lambda_runtime \
        --role $lab_role \
        --handler $1".handler" \
        --zip-file fileb://./empty.zip \
        --environment Variables="{DB_NAME=$db_table_name,BUCKET_NAME=$bucket_name}"
        # --timeout 900
}


lambdas="
get_predict_for_timestamp
get_camera_list
get_images
count_cars
predict_car_count
count_emergency_vehicles
update_vehicles_count
get_station_list
predict_air_quality
get_street_list
check_limits
get_section_list
determine_info
"
for lambda in $lambdas
do
    create_lambda $lambda
done
