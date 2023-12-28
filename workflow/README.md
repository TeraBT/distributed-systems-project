## How to setup the Amazon Step Function

1. Go to Amazon Step Functions
2. Create a blank new state machine
3. In graphical editor, select '{} Code' and paste the content of the file 'stepfunction.json'
4. Replace all Lambda ARNS with your personal Lambda ARNS (that you created previously)
5. Click on 'Create'

## Via setup script

Alternatively you can use the `setup_stepfunction.sh` script if you are using an AWS Educate account.
This script will automatically query the arn's for the lambdas created via the `main_stack_setup.sh` script in `/iac/`.
