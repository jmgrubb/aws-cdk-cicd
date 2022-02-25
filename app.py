#!/usr/bin/env python3
import os
import aws_cdk as cdk
from ml_ops.cicd_stack import CICDStack 
from ml_ops.cicd_iam_stack import CICDIamStack 

app = cdk.App()
env = cdk.Environment(region="eu-west-2")

cicd_iam_stack = CICDIamStack(app, "cicd-iam-stack",
    env=env, 
)

cicd_stack = CICDStack(app, "cicd-stack", 
    env=env,
)

app.synth()
