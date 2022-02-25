# CICD CDK Stacks

This repo deploys the necessary resources for CICD of a MLOps project.

Run this command in all environments (e.g. Dev, Prod, QA, tooling):

```
$ cdk deploy cicd-iam-stack --parameters ToolingAccountID=<enterID>
```

Then run this command in the tooling account:

```
$ cdk deploy cicd-stack --parameters roleArnDev=<enterARN> --parameters roleArnProd=<enterARN> --parameters roleArnQA=<enterARN> --parameters roleArnTooling=<enterARN> --parameters S3BucketNameDev=<enterBucketName> --parameters S3BucketNameProd=<enterBucketName> --parameters S3BucketNameQA=<enterBucketName>
```
