# Setting up Pulumi project
1. Install Pulumi (mac)

       brew install pulumi/tap/pulumi

2. Create directory for project (needs empty directory)

       mkdir poc-py-aws && cd poc-py-aws

3. Login to Pulumi

       pulumi login

4. Create Pulumi project [AWS + Python]

       pulumi new aws-python

5. Write your IaC
6. Preview your infrastructure plan

       pulumi preview

7. Create the infrastrucute

       pulumi up

8. Destroy

       pulumi destroy
       