import subprocess, sys
from dotenv import load_dotenv
load_dotenv()
sys.exit(subprocess.call(["dbt", *sys.argv[1:], "--project-dir", "dbt", "--profiles-dir", "dbt"]))
