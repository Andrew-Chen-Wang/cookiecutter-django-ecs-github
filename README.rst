AWS ECS Deploy
==============

AWS ECS Deploy (hopefully with Blue/Green) using GitHub Actions

.. image:: https://img.shields.io/badge/built%20with-Cookiecutter%20Django-ff69b4.svg
     :target: https://github.com/pydanny/cookiecutter-django/
     :alt: Built with Cookiecutter Django

:License: Apache Software License 2.0

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

Basic Commands
--------------

Setting Up Your Users
^^^^^^^^^^^^^^^^^^^^^

* To create a **normal user account**, just go to Sign Up and fill out the form. Once you submit it, you'll see a "Verify Your E-mail Address" page. Go to your console to see a simulated email verification message. Copy the link into your browser. Now the user's email should be verified and ready to go.

* To create an **superuser account**, use this command::

    $ python manage.py createsuperuser

For convenience, you can keep your normal user logged in on Chrome and your superuser logged in on Firefox (or similar), so that you can see how the site behaves for both kinds of users.

Celery
^^^^^^

This app comes with Celery.

To run a celery worker:

.. code-block:: bash

    cd aws_ecs_deploy
    celery -A config.celery_app worker -l info

Please note: For Celery's import magic to work, it is important *where* the celery commands are run. If you are in the same folder with *manage.py*, you should be right.


Deployment
----------

The following details how to deploy this application.
