import builtins
import os

from aws_cdk import CfnOutput, CustomResource, Stack
from aws_cdk import aws_dynamodb as dynamodb
from aws_cdk import aws_lambda as lambda_
from aws_cdk import aws_s3 as s3
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
            deletion_protection=False,
        )

        central_bucket = s3.Bucket(self, "central_bucket")

        # Lambda functions with attached permissions
        get_predict_for_timestamp = PublicLambda(
            self,
            "get_predict_for_timestamp",
            central_table_name=central_table.table_name,
            central_bucket_name=central_bucket.bucket_name,
        )

        get_camera_list = PublicLambda(
            self,
            "get_camera_list",
            central_table_name=central_table.table_name,
            central_bucket_name=central_bucket.bucket_name,
        )
        central_table.grant_read_data(get_camera_list.function)

        get_images = PublicLambda(
            self,
            "get_images",
            central_table_name=central_table.table_name,
            central_bucket_name=central_bucket.bucket_name,
        )
        central_bucket.grant_read(get_images.function)

        count_cars = PublicLambda(
            self,
            "count_cars",
            central_table_name=central_table.table_name,
            central_bucket_name=central_bucket.bucket_name,
        )
        central_bucket.grant_read(count_cars.function)

        predict_car_count = PublicLambda(
            self,
            "predict_car_count",
            central_table_name=central_table.table_name,
            central_bucket_name=central_bucket.bucket_name,
        )

        count_emergency_vehicles = PublicLambda(
            self,
            "count_emergency_vehicles",
            central_table_name=central_table.table_name,
            central_bucket_name=central_bucket.bucket_name,
        )
        central_bucket.grant_read(count_emergency_vehicles.function)

        update_vehicles_count = PublicLambda(
            self,
            "update_vehicles_count",
            central_table_name=central_table.table_name,
            central_bucket_name=central_bucket.bucket_name,
        )
        central_table.grant_write_data(update_vehicles_count.function)

        get_station_list = PublicLambda(
            self,
            "get_station_list",
            central_table_name=central_table.table_name,
            central_bucket_name=central_bucket.bucket_name,
        )
        central_table.grant_read_data(get_station_list.function)

        predict_air_quality = PublicLambda(
            self,
            "predict_air_quality",
            central_table_name=central_table.table_name,
            central_bucket_name=central_bucket.bucket_name,
        )
        central_table.grant_read_write_data(predict_air_quality.function)

        get_street_list = PublicLambda(
            self,
            "get_street_list",
            central_table_name=central_table.table_name,
            central_bucket_name=central_bucket.bucket_name,
        )
        central_table.grant_read_data(get_street_list.function)

        check_limits = PublicLambda(
            self,
            "check_limits",
            central_table_name=central_table.table_name,
            central_bucket_name=central_bucket.bucket_name,
        )
        central_table.grant_read_write_data(check_limits.function)

        get_section_list = PublicLambda(
            self,
            "get_section_list",
            central_table_name=central_table.table_name,
            central_bucket_name=central_bucket.bucket_name,
        )
        central_table.grant_read_data(get_section_list.function)

        determine_info = PublicLambda(
            self,
            "determine_info",
            central_table_name=central_table.table_name,
            central_bucket_name=central_bucket.bucket_name,
        )
        central_table.grant_read_write_data(determine_info.function)

        # output
        CfnOutput(
            self,
            "get_predict_for_timestamp_url",
            value=get_predict_for_timestamp.url,
        )
        CfnOutput(
            self,
            "get_camera_list_url",
            value=get_camera_list.url,
        )
        CfnOutput(self, "get_images_url", value=get_images.url)
        CfnOutput(self, "count_cars_url", value=count_cars.url)
        CfnOutput(
            self,
            "predict_car_count_url",
            value=predict_car_count.url,
        )
        CfnOutput(
            self,
            "count_emergency_vehicles_url",
            value=count_emergency_vehicles.url,
        )
        CfnOutput(
            self,
            "update_vehicles_count_url",
            value=update_vehicles_count.url,
        )
        CfnOutput(
            self,
            "get_station_list_url",
            value=get_station_list.url,
        )
        CfnOutput(
            self,
            "predict_air_quality_url",
            value=predict_air_quality.url,
        )
        CfnOutput(
            self,
            "get_street_list_url",
            value=get_street_list.url,
        )
        CfnOutput(
            self,
            "check_limits_url",
            value=check_limits.url,
        )
        CfnOutput(
            self,
            "get_section_list_url",
            value=get_section_list.url,
        )
        CfnOutput(
            self,
            "determine_info_url",
            value=determine_info.url,
        )


class PublicLambda(Construct):
    def __init__(
        self, scope: Construct, id: str, central_table_name: str, central_bucket_name: str, **kwargs
    ) -> None:
        super().__init__(scope, id)

        self._function = lambda_.Function(
            self,
            id,
            runtime=lambda_.Runtime.PYTHON_3_11,
            code=lambda_.Code.from_asset(os.path.join(".", "build", id)),
            handler=f"{id}.handler",
            environment={"DB_TABLE": central_table_name, "BUCKET": central_bucket_name},
        )

        self._url = self._function.add_function_url(auth_type=lambda_.FunctionUrlAuthType.NONE)

    @property
    def function(self) -> lambda_.Function:
        return self._function

    @property
    def url(self) -> builtins.str:
        return self._url.url
