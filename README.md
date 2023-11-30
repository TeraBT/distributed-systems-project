# Description

This repository contains all code and resources for the group assignment of the WS2023 PS 703088 Verteilte Systeme.

## Contributors
| Name | Matriculation Number | Student ID |
|---|---|---|
| Christopher BAUMGARTNER-TRÖSCH | 11908149 | csaw4421 |
| Emanuel PRADER | 12116213 | csaz9581 |
| Fabian MARGREITER | 12122376 | csba4402 |
| Lara PICHLER | 12124086 | csba1775 |

# Repository structure

The repository contains the components necessary to setup the service within the AWS cloud. The service combines functional code and infrastructure as code:

- The ***apollo*** directory contains code for the execution of the flow service written in [AFCL](https://apollowf.github.io/)
- The ***build*** directory contains functional code for Lambda functions, etc.
- The ***doc*** directory contains any media and textual information for planning and documenting the service
- The ***iac*** directory contains the AWS CDK Stack defining AWS resources
- The ***scripts*** directory contains miscellaneous helper scripts
- The ***tests*** directory contains unit and integration tests for both functional and infrastructure code

# Installation and setup

## Python

Python is the programming language used for functional and infrastructure code. A working Python 3.11 installation is required on your machine. See [https://www.python.org/downloads/](https://www.python.org/downloads/).

Setup a suitable virtual environment by running `.\scripts\setup_venv.bat` (Linux: `./scripts/setup_venv.sh`). Activate the virtual environment by running `.\.venv\Scripts\activate` (Linux: `source .venv/bin/activate`).

Set the active Python interpreter in VSCode by hitting _Ctrl+Shift+P_, then typing _Python: Select Interpreter_ and choosing the Python executable within the **.venv** directory.

## AWS CDK

The AWS CDK is used for infrastructure as code definition. See [https://docs.aws.amazon.com/cdk/v2/guide/getting_started.html#getting_started_prerequisites](https://docs.aws.amazon.com/cdk/v2/guide/getting_started.html#getting_started_prerequisites) for setup guidance and [https://cdkworkshop.com/30-python.html](https://cdkworkshop.com/30-python.html) for an introductory workshop.

Summary of installation steps (see above links for full guideline):

1. Install Node 14.15.0 or later
2. Install the AWS CDK Toolkit by running `npm install -g aws-cdk` (verify success by running `cdk --version`)
3. Make access credentials to your AWS account available within a shared AWS config file (see [Link 1](https://docs.aws.amazon.com/sdkref/latest/guide/file-format.html) and [Link 2](https://docs.aws.amazon.com/sdkref/latest/guide/file-location.html))
4. Bootstrap your AWS account by running `cdk bootstrap`

**NOTE:** Due to restricted privileges it might not be possible to bootstrap an AWS Academy account. AWS CDK is therefore not useable with such an account and infrastructure will have to be managed manually via the AWS CLI or the AWS Management Console. Any infrastructure definition within the ***iac*** directory should be seen as documentation.

## IDE

> **[IMPORTANT]** To guarantee uniform coding standards VSCode is the only IDE that should be used for development

The repository comes with workspace specific settings to automatically ensure uniform coding standards amongst different developers. When initially opening the project directory VSCode should recommend to install some extensions (popup in lower right corner). Install all of them. Do not adjust any settings. If such a popup is not shown, navigate to the extensions tab (_Ctrl+Shift+X_), type _@recommended_ into the search field and install all workspace recommendations.

### boto3 IntelliSense

boto3 as the AWS SDK might be used within functional code of Lambda functions to interact with other cloud resources. IntelliSense does per default not work with most boto3 classes and methods. If the boto3 extension in VSCode has been installed as described before, IntelliSense can be enabled by the following steps:

1. Hit _Ctrl+Shift+P_ to open the command palette
2. Type _AWS boto3: Quick Start_ and confirm
3. If a popup shows up that this project uses boto3 without code completion, click _Enable boto3 code completion_
4. Wait for the (next) popup in the lower right corner and click the middle button _Install_
5. When prompted to select boto3 services, enable:
    - boto3 common
    - S3
    - Any other AWS service that is used
6. Wait for the installation to complete

IntelliSense should thereafter be available for boto3 classes used within Python code.

# Development workflow

1. Create an issue in GitLab
    - Add a short but understandable title
    - Add more details in the description if necessary
        - The issue should somehow be understandable for others than the author
        - This field can be used to collect ideas, thoughts, etc. regarding the issue
    - Assign a responsible person (or leave unassigned if not possible at the moment)
    - Select one of the predefined milestones
    - Choose one suitable label
        - **Feature**
            - Something that implements a step working towards the goal of the project and produces code
            - Examples:
                - Create function xyz
                - Define S3 bucket specifications 
        - **Task**
            - Something that is necessary for the project, but does not directly produce code
            - Examples:
                - Create a new diagram used for planning and documentation purposes
                - Create the final presentation
                - Do initial training on Apollo
        - **Bug**
            - A bug within the application
            - Add details on how to reproduce the bug in the issue description
            - The issue is completed, when the bug cannot be reproduced anymore
    - Setting a due date is not required

2. Work on the issue
    - Assign yourself as the responsible person
    - Use the GitLab issue to collect notes (if that makes sense)
    - If files are to be changed/created
        - Create a branch out of the main branch, named as `<issue no>-<issue title>` (issue title in lower case, spaces replaced by `-`)
        - Commit and push any changes to that branch

3. Complete the issue
    - If a branch has been created before
        - Select the GitLab issue
        - Create a merge request and assign a reviewer (and inform the reviewer)
        - If reviewer declines merge request, return to step 2
    - If no branch has been created
        - Close the GitLab issue

# Usage

Setup and installation must be completed as described before to run any of the following commands. The Python virtual environment must be active.

## Run unit tests

Run unit tests (without coverage report generation):

```
pytest
```

Run unit test (with coverage report generation - see **htmlcov/index.html**):

```
coverage run -m pytest
coverage html --omit="tests/*"
```

Run specific unit tests (with output enabled):

- Annotate tests to run with @pytest.mark.debug
- Execute:

```
pytest -m debug -s
```
- Remove @pytest.mark.debug annotations again

## Deploy AWS infrastructure

Deploy AWS infrastructure by running `.\scripts\deploy.bat` (Linux: `./scripts/deploy.sh`). Confirm prompts if required.

**NOTE:** This requires a functional AWS CDK installation and a bootstrapped AWS account.

## Undeploy AWS infrastructure

Undeploy AWS infrastructure by running `cdk destroy`. Confirm prompts if required
