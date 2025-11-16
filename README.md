# Find Optimal Time Slot

A **serverless API** to find the optimal meeting time slot for multiple participants based on their preferred time slots. It is deployed to AWS using **Lambda**, **API Gateway**, and managed with **Terraform**. The project includes unit and integration tests with **pytest**, and a CI/CD pipeline via **GitHub Actions** using **OIDC for AWS authentication**.

---

## Features

- Accepts a meeting name and participants with preferred time slots.
- Returns the time slots with the maximum number of participants.
- Handles input validation with error messages.
- CI/CD pipeline with GitHub Actions.
- Manual workflow for destroying AWS infrastructure.

---

## Project Structure

```
├── README.md
├── diagram.png
├── oidc-provider-and-role
│   ├── github-oidc-provider.yaml
│   └── github-oidc-role.yaml
├── optimal_time_slot_lambda
│   ├── build.sh
│   ├── dist
│   │   └── lambda.zip
│   └── src
│       └── optimal_time_slot_lambda.py
├── pytest.ini
├── requirements.txt
├── terraform
│   ├── backend.tf
│   ├── main.tf
│   ├── outputs.tf
│   ├── variables.tf
│   └── versions.tf
└── tests
    ├── integration
    │   └── test_optimal_time_slot_integration.py
    └── unit
        └── test_optimal_time_slot_lambda.py
```

---

## Prerequisites

- **AWS Account** with permissions to resources.
- **Terraform**.
- **Python (used 3.13)** and **pip**.

---

## Setup

1. Clone repository:
```
git clone https://github.com/juunis/find-optimal-time-slot.git
```

2. Create Python virtual environment:
```
python -m venv .venv
source .venv/bin/activate
```

3. Install dependencies:
```
pip install -r requirements.txt
```

---

## Building the Lambda Package

From the project root:
```
./optimal_time_slot_lambda/build.sh
```

This will create dist/lambda.zip ready for deployment.

---

## Running Tests

Unit/Local Tests:
```
pytest tests/local -vv
```

Integration Tests (against deployed API)
```
pytest tests/integration -vv
```
---

## S3 Bucket for Remote State

When deploying via GitHub Actions, it's best to store Terraform state remotely in an **S3 bucket**.

You can create the bucket via AWS CLI, Console or other means. Example using AWS CLI:

```
aws s3 mb s3://<YOUR_BUCKET_NAME> --region eu-west-1
```

Update the bucket name in `terraform/backend.tf` to match your created bucket. **eu-west-1** is the default region in `terraform/variables.tf`. The region must be updated in `terraform/variables.tf` and `.github/workflows/ci-cd.yml` if you choose to deploy in a different region.

---

## Deployment via Command Line

Initialize Terraform:
```
cd terraform
terraform init
```

Validate:
```
terraform validate
```

Plan:
```
terraform plan
```

Apply:
```
terraform apply
```

After applying Terraform, note the api_url output — this is the URL for API calls.

Cleaning up all resources:
```
terraform destroy
```

---

## Deployment via GitHub Actions

### 1. Create the OIDC Provider (if required)

If your AWS account does **not** already have an OIDC provider for GitHub Actions:

Use the provided CloudFormation template: `oidc-provider-and-role/oidc-provider.yaml`.

Deploy it in your AWS account (e.g. via Console or AWS CLI).

### 2. Create the OIDC Role

Use the provided CloudFormation template: `cloudformation/oidc-role.yaml`. This role allows GitHub Actions to deploy your infrastructure.

Deploy the template (e.g. via Console or AWS CLI) and use your AWS Account ID, GitHubOwner, GitHubRepo and GitHubBranch as values for the parameters.

### 3. Add Repository Secret

In your GitHub repository:

Go to **Settings** → **Secrets and variables** → **Actions** → **New repository secret**

Add the following secret:

| Name | Value |
| -------- | ------- |
| AWS_ACCOUNT_ID | Your AWS account ID |

The GitHub Actions workflow uses this secret to assume the OIDC role for deployment.

### Deploy via GitHub Actions

Once your OIDC Provider, OIDC Role and secret are set:

Push to the main branch.

The workflow defined in `.github/workflows/ci-cd.yml` will automatically:

- Run unit tests
- Build the Lambda package
- Deploy the infrastructure via Terraform
- Run integration tests

The destroy workflow defined in `.github/workflows/terraform-destroy.yml` is manual and can be triggered from the workflow view:

**Actions** → **Manual Terraform Destroy** → **Run workflow** → **Enter "DESTROY"** → **Run workflow**

---

## API Usage

The endpoint can be retrieved from the **api_url** Terraform ouput.

**Request Body:**
```
{
  "meetingName": "Design Sync",
  "participants": [
    {
      "name": "Alice",
      "preferredSlots": [
        "2024-06-10T09:00",
        "2024-06-10T10:00",
        "2024-06-10T13:00"
      ]
    },
    {
      "name": "Bob",
      "preferredSlots": [
        "2024-06-10T10:00",
        "2024-06-10T13:00"
      ]
    },
    {
      "name": "Carol",
      "preferredSlots": [
        "2024-06-10T09:00",
        "2024-06-10T10:00"
      ]
    }
  ]
}
```

**meetingName**: Name of the meeting (must be a non-empty string)

**participants**: List of participants with their name and preferredSlots (must be a non-empty list)

**name**: must be non-empty string

**preferredSlots**: must non-empty string in the format "YYYY-MM-DDTHH:MM".

**Response (200 OK):**
```
{
	"meetingName": "Design Sync",
	"optimalSlots": [
		{
			"slot": "2024-06-10T10:00",
			"participants": [
				"Alice",
				"Bob",
				"Carol"
			]
		}
	],
	"maxParticipants": 3
}
```

---

## Ideas for Further Development

- Separate the Lambda handler and logic by moving the handler into one file and the meeting slot calculation into another
- Break up `main.tf` into separate files
- Add linting
- Set up CloudWatch alarms and make a dashboard for monitoring
- Route 53 / custom domain
- API Gateway API keys, usage plans or other methods
- Feature branches and dev, test, prod environments