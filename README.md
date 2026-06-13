
---

# Infrastructure Deployment Guide

## Part 1: Repository Configuration

### Update AWS Account ID in terraform-infra.yml

* Find your 12-digit **Account ID** (top-right corner of AWS Console).
* Update the `OIDC_ROLE_ARN` in `.github/workflows/terraform-infra.yml`:
`arn:aws:iam::YOUR_AWS_ACCOUNT_ID:role/github-actions-terraform-role`


---

## Part 2: Pre-Deployment Setup Checklist in the AWS Console

### 1. Setup OIDC Identity Provider (AWS Console)

1. Log in to the **IAM Console**.
2. Click **Identity providers** (left sidebar) → **Add provider**.
3. Choose **OpenID Connect**.
4. **Provider URL:** `https://token.actions.githubusercontent.com`
5. **Audience:** `sts.amazonaws.com`
6. Click **Add provider**.


### 2.1. Create Custom Managed Policies

1. Log in to the AWS Management Console and navigate to **IAM** → **Policies** → **Create policy**. Click on the JSON tab for each policy, paste the code, and name them accordingly.

## Policy: terraform-backend-permissions
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "TerraformS3BackendAndBootstrap",
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject",
        "s3:ListBucket",
        "s3:CreateBucket",
        "s3:PutBucketVersioning"
      ],
      "Resource": [
        "arn:aws:s3:::tfstate-*-bucket",
        "arn:aws:s3:::tfstate-*-bucket/*"
      ]
    },
    {
      "Sid": "TerraformDynamoDBLockingAndBootstrap",
      "Effect": "Allow",
      "Action": [
        "dynamodb:GetItem",
        "dynamodb:PutItem",
        "dynamodb:DeleteItem",
        "dynamodb:CreateTable",
        "dynamodb:DescribeTable"
      ],
      "Resource": "arn:aws:dynamodb:*:*:table/tflock-*-table"
    }
  ]
}

```


## Policy: terraform-app-infrastructure-permissions
```json
{
	"Version": "2012-10-17",
	"Statement": [
		{
			"Sid": "VPCModulePermissions",
			"Effect": "Allow",
			"Action": [
				"ec2:CreateVpc",
				"ec2:DeleteVpc",
				"ec2:DescribeVpcs",
				"ec2:ModifyVpcAttribute",
				"ec2:CreateSubnet",
				"ec2:DeleteSubnet",
				"ec2:DescribeSubnets",
				"ec2:ModifySubnetAttribute",
				"ec2:CreateInternetGateway",
				"ec2:DeleteInternetGateway",
				"ec2:DescribeInternetGateways",
				"ec2:AttachInternetGateway",
				"ec2:DetachInternetGateway",
				"ec2:CreateRouteTable",
				"ec2:DeleteRouteTable",
				"ec2:DescribeRouteTables",
				"ec2:AssociateRouteTable",
				"ec2:DisassociateRouteTable",
				"ec2:CreateRoute",
				"ec2:DeleteRoute",
				"ec2:CreateSecurityGroup",
				"ec2:DeleteSecurityGroup",
				"ec2:DescribeSecurityGroups",
				"ec2:AuthorizeSecurityGroupIngress",
				"ec2:AuthorizeSecurityGroupEgress",
				"ec2:RevokeSecurityGroupIngress",
				"ec2:RevokeSecurityGroupEgress",
				"ec2:CreateTags",
				"ec2:DescribeVpcAttribute"
			],
			"Resource": "*"
		},
		{
			"Sid": "SecretsManagerPermissions",
			"Effect": "Allow",
			"Action": [
				"secretsmanager:GetSecretValue",
				"secretsmanager:DescribeSecret",
				"secretsmanager:CreateSecret",
				"secretsmanager:DeleteSecret",
				"secretsmanager:PutSecretValue",
				"secretsmanager:GetResourcePolicy"
			],
			"Resource": "arn:aws:secretsmanager:*:*:secret:*"
		},
		{
			"Sid": "DynamoDBTablesPermissions",
			"Effect": "Allow",
			"Action": [
				"dynamodb:CreateTable",
				"dynamodb:DeleteTable",
				"dynamodb:DescribeTable",
				"dynamodb:UpdateTable",
				"dynamodb:TagResource"
			],
			"Resource": [
				"arn:aws:dynamodb:*:*:table/RSVP_Couples",
				"arn:aws:dynamodb:*:*:table/RSVP_Responses"
			]
		},
		{
			"Sid": "CognitoPermissions",
			"Effect": "Allow",
			"Action": [
				"cognito-idp:CreateUserPool",
				"cognito-idp:DeleteUserPool",
				"cognito-idp:DescribeUserPool",
				"cognito-idp:UpdateUserPool",
				"cognito-idp:CreateUserPoolClient",
				"cognito-idp:DeleteUserPoolClient",
				"cognito-idp:DescribeUserPoolClient",
				"cognito-idp:UpdateUserPoolClient",
				"cognito-idp:CreateUserPoolDomain",
				"cognito-idp:DeleteUserPoolDomain",
				"cognito-idp:DescribeUserPoolDomain",
				"cognito-idp:TagResource",
				"cognito-idp:GetUserPoolMfaConfig"
			],
			"Resource": "arn:aws:cognito-idp:*:*:userpool/*"
		},
		{
			"Sid": "IAMManagementForEC2",
			"Effect": "Allow",
			"Action": [
				"iam:CreateRole",
				"iam:DeleteRole",
				"iam:GetRole",
				"iam:UpdateRole",
				"iam:PutRolePolicy",
				"iam:DeleteRolePolicy",
				"iam:GetRolePolicy",
				"iam:CreateInstanceProfile",
				"iam:DeleteInstanceProfile",
				"iam:GetInstanceProfile",
				"iam:AddRoleToInstanceProfile",
				"iam:RemoveRoleFromInstanceProfile",
				"iam:PassRole"
			],
			"Resource": [
				"arn:aws:iam::*:role/ec2_rsvp_role",
				"arn:aws:iam::*:instance-profile/rsvp_ec2_instance_profile"
			]
		},
		{
			"Sid": "EC2AndElasticIPPermissions",
			"Effect": "Allow",
			"Action": [
				"ec2:RunInstances",
				"ec2:TerminateInstances",
				"ec2:DescribeInstances",
				"ec2:AllocateAddress",
				"ec2:ReleaseAddress",
				"ec2:DescribeAddresses",
				"ec2:AssociateAddress",
				"ec2:DisassociateAddress",
				"ec2:CreateTags",
				"ec2:DescribeAddressesAttribute"
			],
			"Resource": "*"
		}
	]
}

```


### 2.2. Create GitHub Actions IAM Role (Manual Console Setup)

1. Go to **IAM** → **Roles** → **Create role**.
2. Select **Custom trust policy** and paste this JSON (replace `YOUR_AWS_ACCOUNT_ID` and `YOUR_GITHUB_USER/YOUR_REPO_NAME`):
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Federated": "arn:aws:iam::YOUR_AWS_ACCOUNT_ID:oidc-provider/token.actions.githubusercontent.com"
      },
      "Action": "sts:AssumeRoleWithWebIdentity",
      "Condition": {
        "StringEquals": { "token.actions.githubusercontent.com:aud": "sts.amazonaws.com" },
        "StringLike": { "token.actions.githubusercontent.com:sub": "repo:BarShenig-Hub/Final_Project_BIU:ref:refs/heads/main" }
      }
    }
  ]
}

```


3. Click **Next**.
4. Search for and check the boxes for: **terraform-backend-permissions** and **terraform-app-infrastructure-permissions**.
5. Click **Next**.
6. Name it `github-actions-terraform-role` and click **Create role**.

### 3. Populate Application Secrets

1. Run the **bootstrap** workflow from your GitHub repository.
2. Navigate to **AWS Secrets Manager** → **Secrets**.
3. Select `rsvp/admin_credentials` → **Retrieve secret value** → **Edit**.
4. Select **Plaintext**, paste the JSON below, and **Save**:
```json
{
  "username": "admin@example.com",
  "password": "YourStrongPassword1",
  "flask_secret_key": "some-long-random-string",
  "ngrok_authtoken": "your-ngrok-token"
}

```
