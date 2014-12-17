API Docs
----------------------------------
http://docs.metricsdashboardgitservice.apiary.io/

Running Locally
---------------
**GITHUB_USERNAME and GITHUB_PASSWORD environment variables must be set!**  
Make git_commit_service your current working directory  

virtualenv env; source env/bin/activate; pip install -r requirements.txt; uwsgi --http 0.0.0.0:8080 --home env --wsgi-file src/git_commit_service.py --callable app --master --enable-threads
