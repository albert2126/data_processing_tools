"""
Different projects use different types of configuration. Each project has its own Git repository in the
organization.
So a repository URL is https://git...../<project-name>/.
For each project (Git repo), the preprocessing scripts need to know:
 1. Project name that must be the same as the name of its Git repository.
 2. Method to retrieve a list of jobs.
 3. Path to retrieve a list of jobs.
 4. Method to retrieve job dependencies.
 5. Path to retrieve job dependencies.
 6. Method to retrieve job data.
 7. Path to retrieve job data.

"""

from utils import get_jobs_akz, get_deps_akz, get_data_ref, get_data_empty

projects = {
    'content-video': {
        'get_job_list': get_jobs_akz,
        'job_list_path': ['content-video/deployment/akz/'],
        'get_job_deps': get_deps_akz,
        'get_project_data': get_data_ref,
        'job_data_path': ['config/config/jobs/common/'],
        'schedule_path': ['content-video/deployment/akz.yml'],
        'get_schedule': get_schedule,
    },
    'content-apps': {
        'get_job_list': get_jobs_akz,
        'job_list_path': [
            'content-apps-orch/deployment/',
            'content-apps-orch/deployment/akz/',
        ],
        'get_job_deps': get_deps_akz,
        'get_project_data': get_data_ref,
        'job_data_path': ['config/config/jobs/common/'],
        'schedule_path': ['content-apps-orch/deployment/akz.yml'],
        'get_schedule': get_schedule,
    },
    'content-coms': {
        'get_job_list': get_jobs_akz,
        'job_list_path': ['content-coms-orch/deployment/akz/'],
        'get_job_deps': get_deps_akz,
        'get_project_data': get_data_empty,
        'job_data_path': ['pie-config/config/jobs/common/'],
        'schedule_path': ['content-coms-orch/deployment/akz.yml'],
        'get_schedule': get_schedule,
    },
}
