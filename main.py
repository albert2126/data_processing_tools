import os
import shutil

from project import Project
from globals import PROJECT_REF, INDEX, PROJECT_REF_INDEX_TMPL, DATA_REF, DATA_REF_INDEX_TMPL,\
    INCLUSIONS_JOBS_PATH, INCLUSIONS_DATA_PATH
from conf.projects import projects


def prepare_ref():
    print(f'Refreshing the project reference documents in {PROJECT_REF}...')
    if os.path.isdir(PROJECT_REF):
        shutil.rmtree(PROJECT_REF)
    os.mkdir(PROJECT_REF)
    shutil.copyfile(PROJECT_REF_INDEX_TMPL, PROJECT_REF + INDEX)
    shutil.copytree(INCLUSIONS_JOBS_PATH, PROJECT_REF + 'inclusions/')
    print(f'Refreshing the data reference documents in {DATA_REF}...')
    if os.path.isdir(DATA_REF):
        shutil.rmtree(DATA_REF)
    os.mkdir(DATA_REF)
    shutil.copyfile(DATA_REF_INDEX_TMPL, DATA_REF + INDEX)
    shutil.copytree(INCLUSIONS_DATA_PATH, DATA_REF + 'inclusions/')


prepare_ref()
for name in projects:
    print(f'\n\nPROCESSING {name}................\n')
    prj = Project(name)
    prj.find_jobs()
    prj.find_data()
    prj.create_docs()
    prj.draw_graphs()
    prj.draw_workflows()
