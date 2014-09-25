git-commit-service.herokuapp.com

Running Locally
---------------
Make git_commit_service your current working directory
virtualenv env; source env/bin/activate; pip install -r requirements.txt; uwsgi --http 0.0.0.0:8080 --home env --wsgi-file src/git_commit_service.py --callable app --master

Pushing to EC2
--------------
Requires the .pem file from EC2 to be in your home directory
Make git_commit_service your current working directory
cd ansible;ansible-playbook -i hosts site.yml --private-key=~/imac.pem;cd ..