
---

# Infrastructure Deployment Guide

## Part 1: Pre-Deployment Setup Checklist

### 1. Setup OIDC Identity Provider (AWS Console)

1. Log in to the **IAM Console**.
2. Click **Identity providers** (left sidebar) → **Add provider**.
3. Choose **OpenID Connect**.
4. **Provider URL:** `https://token.actions.githubusercontent.com`
5. **Audience:** `sts.amazonaws.com`
6. Click **Add provider**.

### 2. Create GitHub Actions IAM Role (Manual Console Setup)

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
**Important: Ensure that the resource "aws_iam_role" inside main.tf is updated with your specific AWS Account ID and GitHub Repository name before running your first deployment, otherwise the Terraform plan will fail to align with your manually created Role.**


3. Click **Next**.
4. Search for and select **AdministratorAccess**. Click **Next**.
5. Name it `github-actions-terraform-role` and click **Create role**.

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



---

## Part 2: For using this repo in your AWS Account and GitHub account

### 1. Update AWS Account ID in GitHub Workflow

* Find your 12-digit **Account ID** (top-right corner of AWS Console).
* Update the `OIDC_ROLE_ARN` in `.github/workflows/terraform.yml`:
`arn:aws:iam::YOUR_AWS_ACCOUNT_ID:role/github-actions-terraform-role`

### 2. Update Repository Identity in `main.tf`

* Open `main.tf` and update the `sub` claim to match your specific GitHub user/repo:
`"token.actions.githubusercontent.com:sub" : "repo:YOUR_GITHUB_USER/YOUR_REPO_NAME:*"`

---