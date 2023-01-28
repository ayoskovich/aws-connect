# aws-connect

Please note that at NO TIME in ANY of this configuration are you hardcoding access keys or token ids or anything like that. This approach does NOT require hardcoding credentials ANYWHERE.

1. Add github as an identity provider. You'll need the ARN in step 3.
    - https://docs.github.com/en/actions/deployment/security-hardening-your-deployments/configuring-openid-connect-in-amazon-web-services

2. Create a policy for the thing you want to do:

3. Create an IAM role for github and attach the policy from step 2:

You can select which branches have access in the Trust Relationship:
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "Federated": "arn:aws:iam::324332189278:oidc-provider/token.actions.githubusercontent.com"
            },
            "Action": "sts:AssumeRoleWithWebIdentity",
            "Condition": {
                "StringEquals": {
                    "token.actions.githubusercontent.com:aud": "sts.amazonaws.com"
                },
                "StringLike": {
                    "token.actions.githubusercontent.com:sub": "repo:ayoskovich/aws-connect:*"
                }
            }
        }
    ]
}
```

4. Create a `yml` workflow file, in this example I tag the image with the commit SHA so you can keep track of that.

```yaml
name: AWS example workflow
on:
  push
env:
  BUCKET_NAME : "ay-airflow"
  AWS_REGION : "us-east-1"
  ECR_REPOSITORY: "github-testing"
  
# permission can be added at job level or workflow level    
permissions:
      id-token: write   # This is required for requesting the JWT
      contents: read    # This is required for actions/checkout
jobs:
  BuildPushImage:
    runs-on: ubuntu-latest
    steps:
      - name: Git clone the repository
        uses: actions/checkout@v3
      - name: Configure aws credentials
        uses: aws-actions/configure-aws-credentials@v1
        with:
          role-to-assume: arn:aws:iam::324332189278:role/github-role
          role-session-name: samplerolesession
          aws-region: us-east-1
      # Upload a file to AWS s3
      #- name:  Copy index.html to s3
      #  run: |
      #    aws s3 cp ./index.html s3://ay-airflow
          
      - name: Login to Amazon ECR
        id: login-ecr
        uses: aws-actions/amazon-ecr-login@aaf69d68aa3fb14c1d5a6be9ac61fe15b48453a2

      - name: Build, tag, and push image to Amazon ECR
        id: build-image
        env:
          ECR_REGISTRY: ${{ steps.login-ecr.outputs.registry }}
          IMAGE_TAG: ${{ github.sha }}
        run: |
          # Build a docker container and
          # push it to ECR so that it can
          # be deployed to ECS.
          docker build -t $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG .
          docker push $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG
          echo "image=$ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG" >> $GITHUB_OUTPUT
```
