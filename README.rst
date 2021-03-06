AWS ECS Deploy
==============

AWS ECS Deploy Blue/Green using GitHub Actions.

Sorry if this didn't work. I tried to do this all in ONE go, or one commit. ~ Andrew C. 29 May 2020. Ripperoni.

Edit: It works! It only took so long... and 3 days of finally realizing it security groups is a thing...
I'm a beginner, so start-ups, take advantage of this repository! ~ Andrew C. 10 June 2020.

Much appreciated code taken from awslabs: https://github.com/awslabs/ecs-nginx-reverse-proxy/tree/master/reverse-proxy

.. image:: https://img.shields.io/badge/built%20with-Cookiecutter%20Django-ff69b4.svg
     :target: https://github.com/pydanny/cookiecutter-django/
     :alt: Built with Cookiecutter Django

:License: Apache Software License 2.0

Table of contents:

- How does this work?
- Deployment Instructions
- Cleanup
- The Caveats in THIS EXAMPLE (easily avoidable)
- Initial Cookiecutter Generation
- Minimal IAM Credentials for ECS
- Minimal IAM Credentials for Deployment
- FAQ

How does this work?
-------------------

The deployment is done through Travis CI which does a sorta webhook to a
GitHub action which will use several AWS GH Actions to finally deploy
your application. TODO Actually create that webhook.

The AWS services that we'll be using are: CodeDeploy, ECS + ECR, Parameter Store,
IAM, Application Load Balancer. CodeDeploy is for deploying from the GH
action. ECS + ECR is where our servers will be located. Parameter store will
be where we store our secrets/environment variables. IAM is for proper
security measures of the credentials given to the server AND to GitHub for deployment.
Yes, we need two IAM users, one for GH and the other for ECS. Finally, we need
ALB for proper Blue/Green deployment assuming you have more than one instance
in your ECS cluster.

I chose ECS because there were GitHub actions for this anyways. However, note
that this is much slower than simply using EC2. The current Travis configuration
uses Docker, but my PR in cookiecutter-django should change the configuration
from Docker based to completely Docker free, erasing 1.5 minutes of CI.

Why not use Fargate? Personally, I like EC2 over Fargate or Lambda since
I use celery a lot. That's really it; I haven't used AWS much, nor have
I actually deployed an AWS app until now.

I've set up an nginx reverse proxy to do a lot of heavy weighted work and to minimize
security risks. Additionally, I've left out several key components like PostgreSQL
and Redis. Those can easily be added in the `aws-task-definition.json`. Just look
at how the rest of the GH action is setup to configure PostgreSQL Dockerfile in
`compose/production/postgres`.

Let's start the deployment process!

Deployment Instructions
-----------------------

The following details how to deploy this application stack to ECS.
If you need to also setup your database and cache, follow 
[issue #9](https://github.com/Andrew-Chen-Wang/cookiecutter-django-ecs-github/issues/9).
You may want to get the hang of the following first, specifically security groups in step 1.
Also note that I didn't write that in the tutorial because it's spare and
came from my memory from a couple months back. I didn't think it was detailed
enough for this tutorial.

It's a lot of instructions since there are so many services:

1. You must have an IAM user with the correct permissions that you can find at the
bottom of this README. Make sure you copy the ones from the section labeled
`Minimal IAM Credentials for Deployment`. You can create a new policy
using the JSON below during the Set Permissions section by pressing
"Attach existing policies directly" and pressing "Create Policy."

Add the IAM user's credentials to your repo's secrets
in the repo's settings. The credentials' names MUST be `AWS_ACCESS_KEY_ID`
and `AWS_SECRET_ACCESS_KEY`

2. Security Groups - Exposing your ports

It took me 10 prolonged days to figure out my security groups were not properly
configured for my ALB and ECS instances. So follow this carefully.

Create a security group called WebAccess with a description saying it's for ALB.

The inbound traffic should be of 4 rules:

- Type HTTP, with custom source type on source 0.0.0.0/0
- Type HTTP, with custom source type on source ::/0
- Type HTTPS, with custom source type on source 0.0.0.0/0
- Type HTTPS, with custom source type on source ::/0

The outbound rules should be left on default, but just in case:

- Type All traffic, destination type Custom at 0.0.0.0/0

Create another security group. This is for your ECS instances.
Name it ECS-reverse-proxy (for another website, I'd recommend
prefixing the name of this with your website name).

The inbound traffic should be 1 rule only:

- Type All Traffic, with custom source type, and find your first security
  group (it should say the name of the security group you just created).

The outbound traffic is the same as the first one.

3. Create two ECR repositories to store your images by running the following:

.. code-block:: shell

    aws ecr create-repository --repository-name nginx-reverse-proxy --region us-east-2
    aws ecr create-repository --repository-name django-app --region us-east-2

Replace the region with your AWS region, and make sure you change it in the
`.github/workflows/aws.yml` file, as well.

4. Create an ECS cluster.
Replace the values for `cluster` in the aws workflow
with your cluster name. The default is "cookiecutter-django".
I guess you could just write that one and not need to change
the one in the GH action.

- Choose EC2 Linux + Networking
- I chose t2.medium for the instance type for enough memory.

  - The task definition uses a limited amount of memory as celery
    isn't a main priority here. As you expand, celery will take up
    more memory and you'll have to increase the memory capacity for
    the Django app, which means you'll have to use a different
    instance type.

- You can just have one instance since Blue/Green deployments
  will provision a new instance and deregister the old one.

  - That's the downfall about ECS. You can configure everything
    in your Dockerfile, but it's a slow build and start time and
    you wish the instance could just simply be updated...

- I had a key pair from previous EC2 usage. You don't necessarily need it
  but it could be helpful to have on in the future. Yes, you can configure
  an ssh key pair in the future.
- Create a new VPC.
- Choose a subnet. Remember which subnet it is.
- Use that second security group that I said was for your ECS instances!
- The IAM role can be the one created by them called ecsInstanceRole.

5. Grant a service trust relationship for newly created IAM role

In order to add our environment variables via our task definition, we must
make sure the IAM role (above, hopefully it was ecsInstanceRole)
can even do a task execution.

Go to your newly created IAM role and click "Trust relationships"

Edit the trust relationship so that, in the "Service" array, you add
`ecs-tasks.amazonaws.com`

5. Buy a website in Route 53.

I bought a random website with a `.de` ending since that came out to be $8.
My website was `asdfasq.de`. Random, ey?

The more random the name and extension, the cheaper.

Change allowed hosts in `config/settings/production.py` to your domain.

Change every instance of asdfasq.de in `compose/production/ecs/nginx/nginx.conf`
to your domain.

6. Configure ACM for https for your domain.

Find ACM (certificate manager) and add your domain and
its www. format, as well.

7. Create the ALB, or Application Load Balancer with ACM

NOTE: I might be missing a step with the certificate manager. I deployed
a test website on EC2 as a standalone, and I might've done something to
properly configure the certificate. PLEASE open a PR/Patch if I'm missing it.

Go to the EC2 page. Find the Load Balancers section and create a new balancer.

- Name your load balancer something like... Joe.
- Add a new listener with HTTPS. The port should autofill itself to be 443.
  Click next.
- Your VPC and subnets should be the same as the ones you
  SHOULD'VE WRITTEN DOWN in step 3 when creating your cluster.
- I'm seeing my website and certificate. If you're not, then look online
  for how to do that and open a PR.
- Your security group is the first one you created in step 2.
- Configure routing:

  - Select new target group
  - Name it something
  - The protocol should be HTTP.
  - Leave health check on default.

- Don't register any instance.
- Finally, create it.

8. Add your load balancer to your hosted zone

Go back to Route 53. Go to your hosted zone and add 2 A record
sets. Choose yes for use alias. Find your load balancer.

The difference between each record set is that the first one
for name can be left blank while the other one should have www.
This is also how you can have multiple ECS clusters for different
applications (i.e. with subdomains).

9. Create a task definition.

Go to the `aws-task-definition.json` file and copy its contents.

In the ECS dashboard, create a new task definition. Scroll to the
bottom until you find "configure via JSON." Paste the contents.

10. Create an ECS service.

After you finished creating your cluster, you should arrive in the service
tab. Create a service.

- Configure Service

  - Launch type is obviously EC2
  - Skip the Task Definition section.
  - Choose your cluster if it's not the one you created.
  - Enter a service name

    - default in workflow is cookiecutter-django-service.
    - If you use the default name, then you don't need to
      change the one in the GH action.

  - Number of tasks is 1
  - The deployments section!

    - Deployment type: Blue/Green

      - I explained up top why I chose this one.
      - Gist of it: CodeDeploy + Websockets + Slow shifting of Traffic.
      - Deployment configuration: ECS Linear 10 Percent Every 1 Minute
      - Service role for CodeDeploy: This is the IAM role that you should
        have for your ECS instances. You can find my configuration down below
        in the IAM role configuration sections with the one labeled `ECS`

  - The service role for CodeDeploy should be the same one you created in step 1.
    It should also, probably, be the only one in that dropdown.

- Configure Network

  - Choose application load balancer
  - Health check grace period should be 15 seconds. This option is above the "choose ALB."
  - For Service IAM Role, I chose AWSServiceRoleForECS. Idk if that'll appear for you though.
  - Select your load balancer
  - Container to Load Balance:

    - Make sure the container name and port is nginx:80
    - Then press `Add to Load Balancer`

      - Disable test listener

  - Choose the target groups you made when making your ALB
    for Target Group 1 and create a second target group.
  - Service discovery

    - Enable it since you've got a website
    - Create a new, verbose private namespace.

      - You want something unique... like cookiecutter-django-namespace1
      - The namespace name can just be left as local

    - The cluster VPC should be the one you had all along.

      - Enable ECS task health propagation
      - DNS records for service discovery should have the
        container with nginx and TTL be 60 seconds.

- Autoscaling policy. I didn't touch it and just said "Do not adjust".
  You can adjust it later. (I honestly have no idea myself. You shouldn't
  need to worry about it yet anyways).
- Review and press that shiny blue button to create the service.

11. Change your health target ports

While you're creating the service, the review stage should show your
new target groups. If not, it's fine. The task will stop and regenerate.

Right click on each target group and change the success codes at the bottom
from `200` to `200,301` (you cannot add spaces).

12. Let's add our environment variables.

Search up Systems Manager. Look for Parameter Store on the left side.
You'll need to add the parameters from `.envs/.production/template.django`.

I've noted which ones you should add.

13. Finally, commit to your repository and let your code be deployed.

Cleanup
-------

If you tested this first on a random GitHub repository, here's how to clean
those resources up:

- You should delete your created IAM roles or users for this test
- Delete your GitHub secrets
- Delete your AWS services. Here's a list, in order, of deletion:

  - Application Load Balancer
  - Target Groups
  - EC2 Instances
  - ECS Service
  - ECS Cluster
  - Task definition
  - CodeDeploy application
  - AWS Cloud Map namespace

The Caveats in THIS EXAMPLE (easily avoidable)
----------------------------------------------

I didn't want to make ANOTHER image just for Celery; instead, I just used:

.. code-block:: shell

    >> celery multi start -A config.celery_app worker beat

I use Sentry to log all my Celery stuff, anyways, and it will come with
cookiecutter-django if you opt-in.

I also use RDS for PostgreSQL and ElastiCache for Redis. You don't HAVE to,
but that would mean you need to configure some more stuff in the
aws-task-definitions.json.

In the task definition, you can easily add the redis and PostgreSQL images. If you
follow the GitHub action of how I set up everything and how you can easily use the
Dockerfile in compose/production/postgres, then just follow how I did the Django app.

Initial Cookiecutter Generation
-------------------------------
.. code-block:: shell

    project_name [My Awesome Project]: AWS ECS Deploy
    project_slug [aws_ecs_deploy]:
    description [Behold My Awesome Project!]: AWS ECS Deploy (hopefully with Blue/Green) using GitHub Actions
    author_name [Daniel Roy Greenfeld]: Andrew Chen Wang
    domain_name [example.com]:
    email [andrew-chen-wang@example.com]: acwangpython@gmail.com
    version [0.1.0]:
    Select open_source_license:
    1 - MIT
    2 - BSD
    3 - GPLv3
    4 - Apache Software License 2.0
    5 - Not open source
    Choose from 1, 2, 3, 4, 5 [1]: 4
    timezone [UTC]:
    windows [n]:
    use_pycharm [n]:
    use_docker [n]: y
    Select postgresql_version:
    1 - 11.3
    2 - 10.8
    3 - 9.6
    4 - 9.5
    5 - 9.4
    Choose from 1, 2, 3, 4, 5 [1]:
    Select js_task_runner:
    1 - None
    2 - Gulp
    Choose from 1, 2 [1]:
    Select cloud_provider:
    1 - AWS
    2 - GCP
    3 - None
    Choose from 1, 2, 3 [1]:
    Select mail_service:
    1 - Mailgun
    2 - Amazon SES
    3 - Mailjet
    4 - Mandrill
    5 - Postmark
    6 - Sendgrid
    7 - SendinBlue
    8 - SparkPost
    9 - Other SMTP
    Choose from 1, 2, 3, 4, 5, 6, 7, 8, 9 [1]: 2
    use_drf [n]:
    custom_bootstrap_compilation [n]:
    use_compressor [n]:
    use_celery [n]: y
    use_mailhog [n]:
    use_sentry [n]:
    use_whitenoise [n]:
    use_heroku [n]:
    Select ci_tool:
    1 - None
    2 - Travis
    3 - Gitlab
    Choose from 1, 2, 3 [1]:
    keep_local_envs_in_vcs [y]:
    debug [n]:

Minimal IAM Credentials for ECS
-------------------------------

You'll need these permissions for your ECS:
- S3 Full Access

Minimal IAM Credentials for Deployment
--------------------------------------

You're probably thinking... wtf is with all these brackets.
Security. Besides that, you can use asterisks for demonstration
for demonstration purposes.

For me, during testing, I just used FullAccess... Shh...

.. code-block:: json

    {
       "Version":"2012-10-17",
       "Statement":[
          {
             "Sid":"RegisterTaskDefinition",
             "Effect":"Allow",
             "Action":[
                "ecs:RegisterTaskDefinition"
             ],
             "Resource":"*"
          },
          {
             "Sid":"PassRolesInTaskDefinition",
             "Effect":"Allow",
             "Action":[
                "iam:PassRole"
             ],
             "Resource":[
                "arn:aws:iam::<aws_account_id>:role/<task_definition_task_role_name>",
                "arn:aws:iam::<aws_account_id>:role/<task_definition_task_execution_role_name>"
             ]
          },
          {
             "Sid":"DeployService",
             "Effect":"Allow",
             "Action":[
                "ecs:DescribeServices",
                "ecs:UpdateService",
                "codedeploy:GetDeploymentGroup",
                "codedeploy:CreateDeployment",
                "codedeploy:GetDeployment",
                "codedeploy:GetDeploymentConfig",
                "codedeploy:RegisterApplicationRevision"
             ],
             "Resource":[
                "arn:aws:ecs:<region>:<aws_account_id>:service/<cluster_name>/<service_name>",
                "arn:aws:codedeploy:<region>:<aws_account_id>:deploymentgroup:<application_name>/<deployment_group_name>",
                "arn:aws:codedeploy:<region>:<aws_account_id>:deploymentconfig:*",
                "arn:aws:codedeploy:<region>:<aws_account_id>:application:<application_name>"
             ]
          }
       ]
    }

FAQ
---

How do I add celery?

Go to `compose/production/ecs/django/start` and add the line

`celery multi start worker beat -A config.celery_app`

If you'd like to troubleshoot your AWS actions, add the
secret `ACTION_STEP_DEBUG` with value `true` to your GitHub repo.

Here is the AWS action doc specifying this https://github.com/aws-actions/amazon-ecs-deploy-task-definition#troubleshooting

What's this license?

Apache 2.0

Best practices?

Rotate your keys!

What if I mess up creating the ECS service?

Got something there's a service already here? I did too,
lol. Search up AWS Cloud Map. Delete the one that says `local`.

You may also have to go to CodeDeploy and delete the Application there, too.

Are you experienced in AWS?

Absolutely not. This would be my first time actually using AWS besides
self hosting on one instace. This was just a nice learning experience that seems sooooo
painful for start ups. In other words, STARTUPS! Get moving! I just gave
you a free repo to copy off of :)

I did play around with AWS trying to use the default cookiecutter-django
before which is why I didn't know how I set up ACM in the first place. It
worked after a painful 12 hours of trying to figure out wtf was going wrong.

Why do you like typing so much?

I like to train my fingers.

Plus, it's nice seeing my painful moments and learning from them.
It's like the cliche standing back and being proud of your work.

But this was a painful 10 hours... I started at 12 and now it's 22:11.

What did you learn from this?

Always start small. On 10 June 2020, I finally figured to try and start
small with a single EC2 with a load balancer (however, I will admit that
I suspected the security groups was an issue for the most part).

On the same day, I finally got it to work. So, always start small, and
then try out this methodology.
