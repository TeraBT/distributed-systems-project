import builtins
import os

from aws_cdk import RemovalPolicy, Stack
from aws_cdk import aws_dynamodb as dynamodb
from aws_cdk import aws_lambda as lambda_
from aws_cdk import aws_s3 as s3
from aws_cdk import aws_stepfunctions as sfn
from aws_cdk import aws_stepfunctions_tasks as tasks
from constructs import Construct

dirname = os.path.dirname(__file__)


class MainStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # central table and bucket
        central_table = dynamodb.Table(
            self,
            "central_table",
            partition_key=dynamodb.Attribute(name="PK", type=dynamodb.AttributeType.STRING),
            sort_key=dynamodb.Attribute(name="SK", type=dynamodb.AttributeType.STRING),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.DESTROY,
        )

        central_bucket = s3.Bucket(self, "central_bucket")

        # Lambda functions with attached permissions
        lambda_env_variables = {
            "DB_NAME": central_table.table_name,
            "BUCKET_NAME": central_bucket.bucket_name,
        }
        get_predict_for_timestamp = WorkflowLambda(
            self, "get_predict_for_timestamp", lambda_env_variables
        )

        get_camera_list = WorkflowLambda(self, "get_camera_list", lambda_env_variables)
        central_table.grant_read_data(get_camera_list.function)

        get_images = WorkflowLambda(self, "get_images", lambda_env_variables)
        central_table.grant_read_data(get_images.function)

        count_cars = WorkflowLambda(self, "count_cars", lambda_env_variables)
        central_bucket.grant_read(count_cars.function)

        predict_car_count = WorkflowLambda(self, "predict_car_count", lambda_env_variables)

        count_emergency_vehicles = WorkflowLambda(
            self, "count_emergency_vehicles", lambda_env_variables
        )
        central_bucket.grant_read(count_emergency_vehicles.function)

        update_vehicles_count = WorkflowLambda(self, "update_vehicles_count", lambda_env_variables)
        central_table.grant_write_data(update_vehicles_count.function)

        get_station_list = WorkflowLambda(self, "get_station_list", lambda_env_variables)
        central_table.grant_read_data(get_station_list.function)

        predict_air_quality = WorkflowLambda(self, "predict_air_quality", lambda_env_variables)
        central_table.grant_read_write_data(predict_air_quality.function)

        get_street_list = WorkflowLambda(self, "get_street_list", lambda_env_variables)
        central_table.grant_read_data(get_street_list.function)

        check_limits = WorkflowLambda(self, "check_limits", lambda_env_variables)
        central_table.grant_read_write_data(check_limits.function)

        get_section_list = WorkflowLambda(self, "get_section_list", lambda_env_variables)
        central_table.grant_read_data(get_section_list.function)

        determine_info = WorkflowLambda(self, "determine_info", lambda_env_variables)
        central_table.grant_read_write_data(determine_info.function)

        # workflow

        workflow_get_predict_for_timestamp = tasks.LambdaInvoke(
            self,
            "Get predict for timestamp",
            lambda_function=get_predict_for_timestamp.function,
            payload_response_only=True,
            result_selector={"predictFor.$": "$"},
        )

        # parallel: analyze-input-data
        workflow_analyze_input_data = sfn.Parallel(
            self, "Analyze input data", result_path=sfn.JsonPath.DISCARD
        )
        # branch 1 of parallel: analyze-input-data
        workflow_get_camera_list = tasks.LambdaInvoke(
            self,
            "Get camera list",
            lambda_function=get_camera_list.function,
            payload_response_only=True,
            result_path="$.cameraIds",
        )
        # parallelFor: analyze-data-per-camera
        workflow_analyze_data_per_camera = sfn.Map(
            self,
            "Analyze data per camera",
            max_concurrency=40,
            items_path="$.cameraIds",
            parameters={"cameraId.$": "$$.Map.Item.Value", "predictFor.$": "$.predictFor"},
        )
        workflow_get_images = tasks.LambdaInvoke(
            self,
            "Get images",
            lambda_function=get_images.function,
            payload_response_only=True,
            result_path="$.imageUris",
        )
        # parallel: count-all-vehicles
        workflow_count_all_vehicles = sfn.Parallel(
            self,
            "Count all vehicles",
            result_selector={
                "carCountPrediction.$": "$[0].carCountPrediction",
                "emergencyVehicleCount.$": "$[1].emergencyVehicleCount",
            },
            result_path="$.counts",
        )
        # branch 1 of parallel: count-all-vehicles
        workflow_count_cars = tasks.LambdaInvoke(
            self,
            "Count cars",
            lambda_function=count_cars.function,
            payload_response_only=True,
            input_path="$.imageUris",
            result_path="$.carCount",
        )
        workflow_predict_car_count = tasks.LambdaInvoke(
            self,
            "Predict car count",
            lambda_function=predict_car_count.function,
            payload_response_only=True,
            result_selector={"carCountPrediction.$": "$"},
        )
        workflow_count_all_vehicles.branch(workflow_count_cars.next(workflow_predict_car_count))
        # branch 2 of parallel: count-all-vehicles
        workflow_count_emergency_vehicles = tasks.LambdaInvoke(
            self,
            "Count emergency vehicles",
            lambda_function=count_emergency_vehicles.function,
            payload_response_only=True,
            input_path="$.imageUris",
            result_selector={"emergencyVehicleCount.$": "$"},
        )
        workflow_count_all_vehicles.branch(workflow_count_emergency_vehicles)
        workflow_update_vehicles_count = tasks.LambdaInvoke(
            self,
            "Update vehicles count",
            lambda_function=update_vehicles_count.function,
            payload_response_only=True,
        )
        workflow_analyze_data_per_camera.iterator(
            workflow_get_images.next(workflow_count_all_vehicles).next(
                workflow_update_vehicles_count
            )
        )
        workflow_analyze_input_data.branch(
            workflow_get_camera_list.next(workflow_analyze_data_per_camera)
        )
        # branch 2 of parallel: analyze-input-data
        workflow_get_station_list = tasks.LambdaInvoke(
            self,
            "Get station list",
            lambda_function=get_station_list.function,
            payload_response_only=True,
            result_path="$.stationIds",
        )
        ## parallelFor: analyze-data-per-station
        workflow_analyze_data_per_station = sfn.Map(
            self,
            "Analyze data per station",
            max_concurrency=40,
            items_path="$.stationIds",
            parameters={"stationId.$": "$$.Map.Item.Value", "predictFor.$": "$.predictFor"},
        )
        workflow_predict_air_quality = tasks.LambdaInvoke(
            self,
            "Predict air quality",
            lambda_function=predict_air_quality.function,
            payload_response_only=True,
        )
        workflow_analyze_data_per_station.iterator(workflow_predict_air_quality)
        workflow_analyze_input_data.branch(
            workflow_get_station_list.next(workflow_analyze_data_per_station)
        )

        workflow_get_street_list = tasks.LambdaInvoke(
            self,
            "Get street list",
            lambda_function=get_street_list.function,
            payload_response_only=True,
            result_path="$.streetIds",
        )

        # parallelFor: check-limits-per-street
        workflow_check_limits_per_street = sfn.Map(
            self,
            "Check limits per street",
            max_concurrency=40,
            items_path="$.streetIds",
            parameters={"streetId.$": "$$.Map.Item.Value", "predictFor.$": "$.predictFor"},
            result_path=sfn.JsonPath.DISCARD,
        )
        workflow_check_limits = tasks.LambdaInvoke(
            self,
            "Check limits",
            lambda_function=check_limits.function,
            payload_response_only=True,
        )
        workflow_check_limits_per_street.iterator(workflow_check_limits)

        workflow_get_section_list = tasks.LambdaInvoke(
            self,
            "Get section list",
            lambda_function=get_section_list.function,
            payload_response_only=True,
            result_path="$.sectionIds",
        )

        # parallelFor: determine-info-per-section
        workflow_determine_info_per_section = sfn.Map(
            self,
            "Determine info per section",
            max_concurrency=40,
            items_path="$.sectionIds",
            parameters={"sectionId.$": "$$.Map.Item.Value", "predictFor.$": "$.predictFor"},
            result_path=sfn.JsonPath.DISCARD,
        )
        workflow_determine_info = tasks.LambdaInvoke(
            self,
            "Determine info",
            lambda_function=determine_info.function,
            payload_response_only=True,
        )
        workflow_determine_info_per_section.iterator(workflow_determine_info)

        # workflow definition
        workflow = (
            workflow_get_predict_for_timestamp.next(workflow_analyze_input_data)
            .next(workflow_get_street_list)
            .next(workflow_check_limits_per_street)
            .next(workflow_get_section_list)
            .next(workflow_determine_info_per_section)
        )

        # state machine
        sfn.StateMachine(
            self, "state_machine", definition_body=sfn.DefinitionBody.from_chainable(workflow)
        )


class WorkflowLambda(Construct):
    def __init__(self, scope: Construct, id: str, env: dict) -> None:
        super().__init__(scope, id)
        self._function = lambda_.Function(
            self,
            id,
            code=lambda_.Code.from_asset(os.path.join(".", "build", id)),
            handler=f"{id}.handler",
            runtime=lambda_.Runtime.PYTHON_3_11,
            environment=env,
        )

    @property
    def function(self):
        return self._function
