from aws_cdk import (
    Duration,
    Stack,
    CfnParameter, 
    aws_s3 as s3,
    aws_codecommit as codecommit,
    aws_codebuild as codebuild, 
    aws_codepipeline as codepipeline,
    aws_codepipeline_actions as cp_actions,
    aws_iam as iam 
)
from constructs import Construct

class CICDStack(Stack):

    def __init__(
        self, 
        scope: Construct, 
        construct_id: str, 
        **kwargs
    ) -> None:

        super().__init__(scope, construct_id, **kwargs)

        role_arn_dev = CfnParameter(self, "roleArnDev", type="String", description="Role ARN dev env")
        role_arn_prod = CfnParameter(self, "roleArnProd", type="String", description="Role ARN prod env")
        role_arn_qa = CfnParameter(self, "roleArnQA", type="String", description="Role ARN QA env")
        role_arn_tooling = CfnParameter(self, "roleArnTooling", type="String", description="Role ARN tooling env")

        s3_bucket_name_dev = CfnParameter(self, "S3BucketNameDev", type="String", description="S3 Bucket dev env")
        s3_bucket_name_prod = CfnParameter(self, "S3BucketNameProd", type="String", description="S3 Bucket prod env")
        s3_bucket_name_qa = CfnParameter(self, "S3BucketNameQA", type="String", description="S3 Bucket qa env")

        # IAM

        tooling_role = iam.Role.from_role_arn(self, "tooling_role",
            role_arn=role_arn_tooling.value_as_string
        )

        # Artifacts bucket
        artifact_bucket = s3.Bucket(self, "artifact-bucket",
            versioned=True,
            encryption=s3.BucketEncryption.S3_MANAGED,
            access_control=s3.BucketAccessControl("BUCKET_OWNER_FULL_CONTROL")
            )
        
        # CodeCommit Repo
        repo = codecommit.Repository(self, "mlops-repo",
            repository_name="MLOps",
        )

        # CodeBuild Project
        # Dev
        project_dev = codebuild.PipelineProject(self, "codebuild-dev",
            timeout=Duration.minutes(480),
            role=tooling_role,
            environment=codebuild.BuildEnvironment(
                compute_type=codebuild.ComputeType.SMALL,
                build_image=codebuild.LinuxBuildImage.from_code_build_image_id("aws/codebuild/standard:5.0"),
                environment_variables={
                    "CROSS_ACCOUNT_ROLE": { "value": role_arn_dev.value_as_string},
                    "ENV": { "value": "Dev"},
                    "S3_BUCKET_NAME": { "value": s3_bucket_name_dev.value_as_string}
                }    
            )
        )  

        # Prod
        project_prod = codebuild.PipelineProject(self, "codebuild-prod",
            timeout=Duration.minutes(480),
            role=tooling_role,
            environment=codebuild.BuildEnvironment(
                compute_type=codebuild.ComputeType.SMALL,
                build_image=codebuild.LinuxBuildImage.from_code_build_image_id("aws/codebuild/standard:5.0"),
                environment_variables={
                    "CROSS_ACCOUNT_ROLE": { "value": role_arn_prod.value_as_string},
                    "ENV": { "value": "Prod"},
                    "S3_BUCKET_NAME": { "value": s3_bucket_name_prod.value_as_string}
                }    
            )
        )

        # QA
        project_QA = codebuild.PipelineProject(self, "codebuild-qa",
            timeout=Duration.minutes(480),
            role=tooling_role,
            environment=codebuild.BuildEnvironment(
                compute_type=codebuild.ComputeType.SMALL,
                build_image=codebuild.LinuxBuildImage.from_code_build_image_id("aws/codebuild/standard:5.0"),
                environment_variables={
                    "CROSS_ACCOUNT_ROLE": { "value": role_arn_qa.value_as_string},
                    "ENV": { "value": "QA"},
                    "S3_BUCKET_NAME": { "value": s3_bucket_name_qa.value_as_string}
                }    
            )
        )

        # CodePipeline
        # Dev
        pipeline_dev = codepipeline.Pipeline(self, "tooling-pipeline-dev",
            pipeline_name="ToolingPipelineDev",
            role=tooling_role,
            branch="dev",
            artifact_bucket=artifact_bucket,
        )

        source_output_dev = codepipeline.Artifact()
        source_action_dev = cp_actions.CodeCommitSourceAction(
            action_name="CodeCommit",
            repository=repo,
            output=source_output_dev
        )
        pipeline_dev.add_stage(
            stage_name="Source",
            actions=[source_action_dev]
        )       

        build_action = cp_actions.CodeBuildAction(
            action_name="CodeBuild",
            project=project_dev,
            input=source_output_dev,
        )
        
        pipeline_dev.add_stage(
            stage_name="Build",
            actions=[build_action],
        )  

        # Prod
        pipeline_prod = codepipeline.Pipeline(self, "tooling-pipeline-prod",
            pipeline_name="ToolingPipelineProd",
            role=tooling_role,
            artifact_bucket=artifact_bucket,
        )

        source_output_prod = codepipeline.Artifact()
        source_action_prod = cp_actions.CodeCommitSourceAction(
            action_name="CodeCommit",
            repository=repo,
            output=source_output_prod
        )
        pipeline_prod.add_stage(
            stage_name="Source",
            actions=[source_action_prod]
        )       

        build_action = cp_actions.CodeBuildAction(
            action_name="CodeBuild",
            project=project_prod,
            input=source_output_prod,
        )
        
        pipeline_prod.add_stage(
            stage_name="Build",
            actions=[build_action],
        )  

        # QA
        pipeline_QA = codepipeline.Pipeline(self, "tooling-pipeline-qa",
            pipeline_name="ToolingPipelineQA",
            role=tooling_role,
            branch="qa",
            artifact_bucket=artifact_bucket,
        )

        source_output_QA = codepipeline.Artifact()
        source_action_QA = cp_actions.CodeCommitSourceAction(
            action_name="CodeCommit",
            repository=repo,
            output=source_output_QA
        )
        pipeline_QA.add_stage(
            stage_name="Source",
            actions=[source_action_QA]
        )       

        build_action = cp_actions.CodeBuildAction(
            action_name="CodeBuild",
            project=project_QA,
            input=source_output_QA,
        )
        
        pipeline_QA.add_stage(
            stage_name="Build",
            actions=[build_action],
        )  
   
