import json
import os
from pathlib import Path
from string import Template
import yaml
import pprint
from pyhocon import ConfigFactory
import re

from globals import SCHEMA_PATH

rx_cln = re.compile(r'include.*')
pp = pprint.PrettyPrinter(indent=2)


def read_yaml(path):
    with open(path) as stream:
        try:
            return yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)


def read_hocon(path):
    with open(path) as fd:
        # Suppress warnings caused by the 'include' directive:
        conf_str = rx_cln.sub('', fd.read())
    return ConfigFactory.parse_string(conf_str, resolve=False)


def read_json_schema(schema):
    if os.path.isfile(SCHEMA_PATH + schema + '.json'):
        with open(SCHEMA_PATH + schema + '.json') as fd:
            config = json.load(fd)
            pk = config.get('primary-key', '')
            if 'columns' in config:
                cols = config['columns']
            elif 'fields' in config:
                cols = config['fields']
            else:
                cols = []
            return pk, cols


# Remove specified prefixes from a word:
def remove_prefixes(word, *prefixes):
    # Remove the longest prefix first:
    prefixes = sorted(prefixes, key=lambda x: len(x), reverse=True)
    for pref in prefixes:
        if word.startswith(pref):
            word = word.replace(pref, '')
    return word


# Replace a specified prefix:
def replace_prefix(word, old, new):
    return word if len(word) == 1 or not word.startswith(old) else new + word[len(old):]


# Replace a specified suffix:
def replace_suffix(word, old, new):
    return word if not word.endswith(old) else word[0: len(word) - len(old)] + new


def create_file_by_template(src, dst, mapping):
    with open(src, 'r') as ifd:
        with open(dst, 'w') as ofd:
            for line in ifd:
                ofd.write(Template(line).substitute(mapping))


# Convert as in this example: pro-ref-app-s-bundle -> Bundle
def job2conf(name):
    return ''.join([word.title() for word in remove_prefixes(name, 'pro-', 'pro-ref-').split('-')])


def compare_jobs_w_driver(driver_name, job_names):
    for j_name in job_names:
        if all(word in driver_name for word in j_name.split('-')):
            return j_name


def add_data_to_project(project_data, job, output_data, input_data):
    job.output = output_data
    job.input = input_data
    for ds in output_data:
        if ds not in project_data.data:
            project_data.data[ds] = {'input_job': job}
        else:
            project_data.data[ds]['input_job'] = job
    for ds in input_data:
        if ds not in project_data.data:
            project_data.data[ds] = {'output_jobs': [job]}
        elif 'output_jobs' not in project_data.data[ds]:
            project_data.data[ds]['output_jobs'] = [job]
        else:
            project_data.data[ds]['output_jobs'].append(job)


# Utils for finding jobs and their dependencies
# Get a list of jobs in a project
def get_jobs_akz(path):
    return {f.name.replace('.job', ''): f for f in Path(path).rglob('*.job')}


# Get job dependencies
def get_deps_akz(path):
    with open(path, 'r') as inpf:
        deps = [d.strip().replace('dependencies=', '') for d in inpf.readlines() if
                d.startswith('dependencies=')]
        return deps[0].split(',') if len(deps) > 0 else []


# Get job data:
def get_data_empty(jobs, project_data, config_path):
    pass


def get_data_ref(jobs, project_data, config_path):
    job_cuts = {job2conf(name): job for name, job in jobs.items()}
    for dir_name in os.listdir(config_path):
        if dir_name in job_cuts:
            data_path = config_path + dir_name
            input_data, output_data = [], []
            for path, folders, files in os.walk(data_path):
                for file_name in files:
                    if file_name == 'application.conf':
                        conf = read_hocon(path + '/' + file_name)
                        input_data = input_data + conf.get('configurator.driver.generic-job.required-datasets', [])
                        output_data = output_data + [ds['name'] for ds in conf.get('configurator.content.datasets-info', [])]
                        umc_ds = conf.get('configurator.umc.dataset-name', '')
                        if umc_ds:
                            output_data.append(umc_ds)
                        add_data_to_project(project_data, job_cuts[dir_name], output_data, input_data)


def get_data_apps(jobs, project_data, config_path):
    job_cuts = {name.replace('pro-', '').replace('kube-', ''): job for name, job in jobs.items()}
    sorted_cut_job_names = sorted(job_cuts, key=len, reverse=True)
    for path, folders, files in os.walk(config_path):
        if 'application.conf' in files:
            conf = read_hocon(path + '/application.conf')
            name = conf.get('configurator.driver.generic-job.name')
            # For each Job:
            for tokens in sorted_cut_job_names:
                out_data = ''
                input_data = []
                if all([token in name for token in tokens.split('-')]):
                    for key in conf.configurator:
                        if not key.startswith('driver'):
                            l1_keys = list(conf.configurator[key].keys())
                            if 'builder' in l1_keys:
                                builder = conf.configurator[key]['builder']
                                out_data = builder.get('name', '')
                                input_data = [item['name'] for item in builder.get('input', [])]
                            elif 'builder' in conf.configurator[key][l1_keys[0]]:
                                builder = conf.configurator[key][l1_keys[0]]['builder']
                                out_data = builder.get('name', '')
                                input_data = [item['name'] for item in builder.get('input', [])]
                            elif 'dataset' in conf.configurator[key]:
                                dataset = conf.configurator
                                out_data = dataset.get('dataset-name', '')
                                input_data = []
                            output_data = [out_data] if out_data else []
                            add_data_to_project(project_data, job_cuts[tokens], output_data, input_data)


def get_empty(paths):
    return {}
