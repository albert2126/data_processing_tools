import os.path

URL_GIT_BASE = 'https://github..../repo/'
HMS_DATABASE_OUTPUT = 'content_output'
HMS_DATABASE_INPUT = 'content_input'
HMS_BASE_URL = 'https://metastore...../metastore/prod/catalog/hive/database/%(db)s/table/%(table)s/'

# Absolute paths:
REPO_DOC = os.path.abspath(f'{os.path.abspath(__file__)}/../../../../') + '/'
REPO_BASE = REPO_DOC + '../'
REPO_BRANCH = 'main'
CONTENT_REF = REPO_BASE + 'content-reference/'
CONTENT_REF_SCH_CONFIG_JOBS_COMMON = CONTENT_REF + 'sch-config/config/jobs/common/'
CONTENT_REF_ORCH = CONTENT_REF + 'content-reference-orchestrator/'

# Relative paths:
ORCH = 'content-reference-orchestrator/'
SCH_CONFIG_JOBS_COMMON = 'sch-config/config/jobs/common/'
ORCH_DEPL_MISC_MELODY = ORCH + 'deployment/config/MELODY/'
ORCH_DEPL_WOW_SCH = ORCH + 'deployment/wow/sch/'

# Documentation:
INDEX = 'index.rst'
DOC_BASE = REPO_DOC + 'docs/source/'
REFERENCE = DOC_BASE + 'reference/'
PROJECT_REF = REFERENCE + 'projects/'
PROJECT_REF_INDEX = PROJECT_REF + INDEX
DATA_REF = REFERENCE + 'data/'
DATA_REF_INDEX = DATA_REF + INDEX

# Graphs:
GRAPH_FILE_SUFFIX = '_flow'

# Document templates:
TOOLS = DOC_BASE + '_tools/'
TEMPLATES = TOOLS + 'templates/'
TEMPLATE_PROJECT_INDEX = TEMPLATES + 'project.tmpl'
PROJECT_REF_INDEX_TMPL = TEMPLATES + 'prj_index.rst_'
TEMPLATE_JOB = TEMPLATES + 'job.tmpl'
DATA_REF_INDEX_TMPL = TEMPLATES + 'data_index.rst_'
TEMPLATE_PROJECT_DATA = TEMPLATES + 'data_project_index.tmpl'
TEMPLATE_DATA = TEMPLATES + 'data.tmpl'
INCLUSIONS_JOBS_PATH = TOOLS + 'inclusions/jobs/'
INCLUSIONS_DATA_PATH = TOOLS + 'inclusions/data/'
INCLUSIONS_JOBS = [name.replace('.txt', '') for name in os.listdir(INCLUSIONS_JOBS_PATH)]
INCLUSIONS_DATA = [name.replace('.txt', '') for name in os.listdir(INCLUSIONS_DATA_PATH)]

# Dataset schemas:
SCHEMA_PATH = ''

# Authentication:
KEY_FILE = '/Users/abagdasarian/secret/s-account-key.txt'
SYSTEM_ACCOUNT = 'core-content'
ENVIRONMENT = 'PROD'

