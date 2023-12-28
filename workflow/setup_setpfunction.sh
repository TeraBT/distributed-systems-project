#!/usr/bin/env bash

query_lambda_arn () {
    aws lambda get-function --function-name $1 --query 'Configuration.FunctionArn' --output text
}

lab_role=$(
aws iam get-role \
    --role-name LabRole \
    --query 'Role.Arn' \
    --output text
)

aws stepfunctions create-state-machine \
    --name traffic_prediction_workflow \
    --role-arn $lab_role \
    --definition '{
    "StartAt": "Get predict for timestamp",
    "States": {
      "Get predict for timestamp": {
        "Next": "Analyze input data",
        "Retry": [
          {
            "ErrorEquals": [
              "Lambda.ClientExecutionTimeoutException",
              "Lambda.ServiceException",
              "Lambda.AWSLambdaException",
              "Lambda.SdkClientException"
            ],
            "IntervalSeconds": 2,
            "MaxAttempts": 6,
            "BackoffRate": 2
          }
        ],
        "Type": "Task",
        "ResultSelector": {
          "predictFor.$": "$"
        },
        "Resource": "'"$(query_lambda_arn get_predict_for_timestamp)"'"
      },
      "Analyze input data": {
        "Type": "Parallel",
        "ResultPath": null,
        "Next": "Get street list",
        "Branches": [
          {
            "StartAt": "Get camera list",
            "States": {
              "Get camera list": {
                "Next": "Analyze data per camera",
                "Retry": [
                  {
                    "ErrorEquals": [
                      "Lambda.ClientExecutionTimeoutException",
                      "Lambda.ServiceException",
                      "Lambda.AWSLambdaException",
                      "Lambda.SdkClientException"
                    ],
                    "IntervalSeconds": 2,
                    "MaxAttempts": 6,
                    "BackoffRate": 2
                  }
                ],
                "Type": "Task",
                "ResultPath": "$.cameraIds",
                "Resource": "'"$(query_lambda_arn get_camera_list)"'"
              },
              "Analyze data per camera": {
                "Type": "Map",
                "End": true,
                "Parameters": {
                  "cameraId.$": "$$.Map.Item.Value",
                  "predictFor.$": "$.predictFor"
                },
                "Iterator": {
                  "StartAt": "Get images",
                  "States": {
                    "Get images": {
                      "Next": "Count all vehicles",
                      "Retry": [
                        {
                          "ErrorEquals": [
                            "Lambda.ClientExecutionTimeoutException",
                            "Lambda.ServiceException",
                            "Lambda.AWSLambdaException",
                            "Lambda.SdkClientException"
                          ],
                          "IntervalSeconds": 2,
                          "MaxAttempts": 6,
                          "BackoffRate": 2
                        }
                      ],
                      "Type": "Task",
                      "ResultPath": "$.imageUris",
                      "Resource": "'"$(query_lambda_arn get_images)"'"
                    },
                    "Count all vehicles": {
                      "Type": "Parallel",
                      "ResultPath": "$.counts",
                      "Next": "Update vehicles count",
                      "Branches": [
                        {
                          "StartAt": "Count cars",
                          "States": {
                            "Count cars": {
                              "Next": "Predict car count",
                              "Retry": [
                                {
                                  "ErrorEquals": [
                                    "Lambda.ClientExecutionTimeoutException",
                                    "Lambda.ServiceException",
                                    "Lambda.AWSLambdaException",
                                    "Lambda.SdkClientException"
                                  ],
                                  "IntervalSeconds": 2,
                                  "MaxAttempts": 6,
                                  "BackoffRate": 2
                                }
                              ],
                              "Type": "Task",
                              "InputPath": "$.imageUris",
                              "ResultPath": "$.carCount",
                              "Resource": "'"$(query_lambda_arn count_cars)"'"

                            },
                            "Predict car count": {
                              "End": true,
                              "Retry": [
                                {
                                  "ErrorEquals": [
                                    "Lambda.ClientExecutionTimeoutException",
                                    "Lambda.ServiceException",
                                    "Lambda.AWSLambdaException",
                                    "Lambda.SdkClientException"
                                  ],
                                  "IntervalSeconds": 2,
                                  "MaxAttempts": 6,
                                  "BackoffRate": 2
                                }
                              ],
                              "Type": "Task",
                              "ResultSelector": {
                                "carCountPrediction.$": "$"
                              },
                              "Resource": "'"$(query_lambda_arn predict_car_count)"'"
                            }
                          }
                        },
                        {
                          "StartAt": "Count emergency vehicles",
                          "States": {
                            "Count emergency vehicles": {
                              "End": true,
                              "Retry": [
                                {
                                  "ErrorEquals": [
                                    "Lambda.ClientExecutionTimeoutException",
                                    "Lambda.ServiceException",
                                    "Lambda.AWSLambdaException",
                                    "Lambda.SdkClientException"
                                  ],
                                  "IntervalSeconds": 2,
                                  "MaxAttempts": 6,
                                  "BackoffRate": 2
                                }
                              ],
                              "Type": "Task",
                              "InputPath": "$.imageUris",
                              "ResultSelector": {
                                "emergencyVehicleCount.$": "$"
                              },
                              "Resource": "'"$(query_lambda_arn count_emergency_vehicles)"'"
                            }
                          }
                        }
                      ],
                      "ResultSelector": {
                        "carCountPrediction.$": "$[0].carCountPrediction",
                        "emergencyVehicleCount.$": "$[1].emergencyVehicleCount"
                      }
                    },
                    "Update vehicles count": {
                      "End": true,
                      "Retry": [
                        {
                          "ErrorEquals": [
                            "Lambda.ClientExecutionTimeoutException",
                            "Lambda.ServiceException",
                            "Lambda.AWSLambdaException",
                            "Lambda.SdkClientException"
                          ],
                          "IntervalSeconds": 2,
                          "MaxAttempts": 6,
                          "BackoffRate": 2
                        }
                      ],
                      "Type": "Task",
                      "Resource": "'"$(query_lambda_arn update_vehicles_count)"'"
                    }
                  }
                },
                "ItemsPath": "$.cameraIds",
                "MaxConcurrency": 40
              }
            }
          },
          {
            "StartAt": "Get station list",
            "States": {
              "Get station list": {
                "Next": "Analyze data per station",
                "Retry": [
                  {
                    "ErrorEquals": [
                      "Lambda.ClientExecutionTimeoutException",
                      "Lambda.ServiceException",
                      "Lambda.AWSLambdaException",
                      "Lambda.SdkClientException"
                    ],
                    "IntervalSeconds": 2,
                    "MaxAttempts": 6,
                    "BackoffRate": 2
                  }
                ],
                "Type": "Task",
                "ResultPath": "$.stationIds",
                "Resource": "'"$(query_lambda_arn get_station_list)"'"
              },
              "Analyze data per station": {
                "Type": "Map",
                "End": true,
                "Parameters": {
                  "stationId.$": "$$.Map.Item.Value",
                  "predictFor.$": "$.predictFor"
                },
                "Iterator": {
                  "StartAt": "Predict air quality",
                  "States": {
                    "Predict air quality": {
                      "End": true,
                      "Retry": [
                        {
                          "ErrorEquals": [
                            "Lambda.ClientExecutionTimeoutException",
                            "Lambda.ServiceException",
                            "Lambda.AWSLambdaException",
                            "Lambda.SdkClientException"
                          ],
                          "IntervalSeconds": 2,
                          "MaxAttempts": 6,
                          "BackoffRate": 2
                        }
                      ],
                      "Type": "Task",
                      "Resource": "'"$(query_lambda_arn predict_air_quality)"'"
                    }
                  }
                },
                "ItemsPath": "$.stationIds",
                "MaxConcurrency": 40
              }
            }
          }
        ]
      },
      "Get street list": {
        "Next": "Check limits per street",
        "Retry": [
          {
            "ErrorEquals": [
              "Lambda.ClientExecutionTimeoutException",
              "Lambda.ServiceException",
              "Lambda.AWSLambdaException",
              "Lambda.SdkClientException"
            ],
            "IntervalSeconds": 2,
            "MaxAttempts": 6,
            "BackoffRate": 2
          }
        ],
        "Type": "Task",
        "ResultPath": "$.streetIds",
        "Resource": "'"$(query_lambda_arn get_street_list)"'"
      },
      "Check limits per street": {
        "Type": "Map",
        "ResultPath": null,
        "Next": "Get section list",
        "Parameters": {
          "streetId.$": "$$.Map.Item.Value",
          "predictFor.$": "$.predictFor"
        },
        "Iterator": {
          "StartAt": "Check limits",
          "States": {
            "Check limits": {
              "End": true,
              "Retry": [
                {
                  "ErrorEquals": [
                    "Lambda.ClientExecutionTimeoutException",
                    "Lambda.ServiceException",
                    "Lambda.AWSLambdaException",
                    "Lambda.SdkClientException"
                  ],
                  "IntervalSeconds": 2,
                  "MaxAttempts": 6,
                  "BackoffRate": 2
                }
              ],
              "Type": "Task",
              "Resource": "'"$(query_lambda_arn check_limits)"'"
            }
          }
        },
        "ItemsPath": "$.streetIds",
        "MaxConcurrency": 40
      },
      "Get section list": {
        "Next": "Determine info per section",
        "Retry": [
          {
            "ErrorEquals": [
              "Lambda.ClientExecutionTimeoutException",
              "Lambda.ServiceException",
              "Lambda.AWSLambdaException",
              "Lambda.SdkClientException"
            ],
            "IntervalSeconds": 2,
            "MaxAttempts": 6,
            "BackoffRate": 2
          }
        ],
        "Type": "Task",
        "ResultPath": "$.sectionIds",
        "Resource": "'"$(query_lambda_arn get_section_list)"'"
      },
      "Determine info per section": {
        "Type": "Map",
        "ResultPath": null,
        "End": true,
        "Parameters": {
          "sectionId.$": "$$.Map.Item.Value",
          "predictFor.$": "$.predictFor"
        },
        "Iterator": {
          "StartAt": "Determine info",
          "States": {
            "Determine info": {
              "End": true,
              "Retry": [
                {
                  "ErrorEquals": [
                    "Lambda.ClientExecutionTimeoutException",
                    "Lambda.ServiceException",
                    "Lambda.AWSLambdaException",
                    "Lambda.SdkClientException"
                  ],
                  "IntervalSeconds": 2,
                  "MaxAttempts": 6,
                  "BackoffRate": 2
                }
              ],
              "Type": "Task",
              "Resource": "'"$(query_lambda_arn determine_info)"'"
            }
          }
        },
        "ItemsPath": "$.sectionIds",
        "MaxConcurrency": 40
      }
    }
  }'
