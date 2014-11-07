Adding repository to tracking list
----------------------------------
curl -i http://ec2-54-208-64-116.compute-1.amazonaws.com/ -d '{"repo":"<repo>"}' -X POST
where <repo> is the user/repository_slug such as "mdotson/git_commit_service"

Running Locally
---------------
**GITHUB_USERNAME and GITHUB_PASSWORD environment variables must be set!**
Make git_commit_service your current working directory
virtualenv env; source env/bin/activate; pip install -r requirements.txt; uwsgi --http 0.0.0.0:8080 --home env --wsgi-file src/git_commit_service.py --callable app --master --enable-threads

Pushing to Cluster
--------------
**GITHUB_USERNAME and GITHUB_PASSWORD environment variables must be set!**
Requires the .pem file from EC2 to be in your home directory
Make git_commit_service your current working directory
cd ansible;ansible-playbook -i hosts site.yml --private-key=~/imac.pem;cd ..

Logging Into EC2 Instance
-------------------------
Download pem file from EC2 and move to HOME directory
ssh -i ~/imac.pem ubuntu@ec2-54-208-64-116.compute-1.amazonaws.com