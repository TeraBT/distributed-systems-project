#!/usr/bin/env python3
import os

import aws_cdk as cdk

from iac.main_stack import MainStack


app = cdk.App()
MainStack(app, "MainStack")

app.synth()
