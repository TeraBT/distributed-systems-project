import aws_cdk as core
import aws_cdk.assertions as assertions
import pytest

from iac.main_stack import MainStack


# example tests. To run these tests, uncomment this file along with the example
# resource in iac/main_stack.py
@pytest.mark.debug
def test_sqs_queue_created():
    app = core.App()
    stack = MainStack(app, "MainStack")
    template = assertions.Template.from_stack(stack)


#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
