

ssh -i ~/imac.pem ubuntu@ec2-54-208-64-116.compute-1.amazonaws.com

Running Locally
---------------
Make git_commit_service your current working directory
virtualenv env; source env/bin/activate; pip install -r requirements.txt; uwsgi --http 0.0.0.0:8080 --home env --wsgi-file src/git_commit_service.py --callable app --master --enable-threads

Pushing to EC2
--------------
Requires the .pem file from EC2 to be in your home directory
Make git_commit_service your current working directory
cd ansible;ansible-playbook -i hosts site.yml --private-key=~/imac.pem;cd ..


curl -i localhost:8080 -d '{"repo":"torvalds/linux"}' -X POST