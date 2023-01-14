import os
import errno
from graphviz import Digraph
import pprint
pp = pprint.PrettyPrinter(indent=2)

from data import ProjectData
from utils import create_file_by_template
from globals import REPO_BASE, PROJECT_REF, \
    PROJECT_REF_INDEX, TEMPLATE_JOB, INDEX, GRAPH_FILE_SUFFIX, TEMPLATE_PROJECT_INDEX, URL_GIT_BASE, INCLUSIONS_JOBS
from conf.projects import projects



class Job:
    def __init__(self, name, conf_file, project_name):
        self.name = name
        self.project_name = project_name
        self.conf_file = conf_file
        self.deps = []
        self.input = []
        self.output = []
        self.schedule = ''
        self.doc_folder = ''
        self.doc_path = ''
        self.graph_name = self.doc_folder + self.name + GRAPH_FILE_SUFFIX

    def find_deps(self, func):
        self.deps = func(self.conf_file)

    def add_schedule(self):
        sch = self.schedule.split()
        if len(sch) == 6:
            sch.append('*')
        with open(self.doc_path, 'a') as fd:
            fd.write('**Scheduledr**:\n\n')
            fd.write('.. list-table::\n')
            fd.write('   :widths: 1 1 1 1 1 1 1\n')
            fd.write('   :header-rows: 1\n\n')
            # fd.write('   :stub-columns: 1\n\n')
            fd.write('   *  -   Sec\n')
            for word in ('Min', 'Hour', 'Day of month', 'Month', 'Day of week', 'Year'):
                fd.write(f'      -   {word}\n')
            fd.write(f'   *  -   `{sch[0]}`\n')
            for word in sch[1:]:
                # word = replace_prefix(word, '*', r'\*')
                fd.write(f'      -   `{word}`\n')
            fd.write('\nThe schedule format is based on ' +
                     ':href:`Cron Expressions<https://docs.oracle.com/cd/E12058_01/doc/doc.1014/e12030/cron_expressions.htm>`.'
                     + ' To decipher it, you can also use ' +
                     ':href:`online formatter<https://freeformatter.com/cron-expression-generator-quartz.html>`.\n\n')

    def create_doc(self, path):
        self.doc_folder = path
        self.doc_path = path + self.name + '.rst'
        inclusion = f'../inclusions/{self.name}.txt' if self.name in INCLUSIONS_JOBS \
            else '../inclusions/empty.txt'
        mapping = {
            'name': self.name,
            'h1_underscore': '#' * len(self.name),
            'filename': self.name + GRAPH_FILE_SUFFIX + '.svg',
            'inclusion': inclusion,
        }
        with open(path + INDEX, 'a') as fd:
            fd.write(f'   {self.name}\n')
        if not os.path.isdir(self.doc_path):
            create_file_by_template(TEMPLATE_JOB, self.doc_path, mapping)
        if self.schedule:
            self.add_schedule()

    def draw_graphs(self):
        dot = Digraph(
            filename=self.graph_name,
            format='svg',
            comment=f'Job flow for {self.name}',
            graph_attr={'rankdir': 'LR'},
            node_attr={'style': 'filled', 'shape': 'cds', 'width': '3'}
        )
        # Draw nodes and edges:
        dot.node(
            self.name,
            color='cadetblue4',
            fillcolor='cadetblue',
            fontcolor='white',
        )
        for dep in self.deps:
            dot.node(
                dep,
                color='cadetblue2',
                fillcolor='cadetblue1',
                href='../' + dep + '/',
                target='_top',
            )
            dot.edge(dep, self.name)
        for idata in self.input:
            dot.node(
                idata,
                shape='folder',
                color='cornsilk3',
                fillcolor='cornsilk',
                href='../../../data/' + self.project_name + '/' + idata + '/',
            )
            dot.edge(idata, self.name)
        for output in self.output:
            dot.node(
                output,
                shape='folder',
                color='cornsilk3',
                fillcolor='cornsilk',
                href='../../../data/' + self.project_name + '/' + output + '/',
            )
            dot.edge(self.name, output)
        dot.render(directory=self.doc_folder)
        os.remove(self.doc_folder + self.graph_name)


class Project:
    def __init__(self, name):
        self.name = name
        self.repo_path = REPO_BASE + name + '/'
        print(f'Processing Git Repo {self.repo_path}............')
        if not os.path.isdir(self.repo_path):
            raise FileNotFoundError(
                errno.ENOENT, os.strerror(errno.ENOENT), REPO_BASE + name
            )
        conf = projects[self.name]
        self.job_paths = (self.repo_path + path for path in conf['job_list_path'])
        self.data_paths = (self.repo_path + path for path in conf['job_data_path'])
        self.schedule_paths = (self.repo_path + path for path in conf['schedule_path'])
        self.get_jobs = conf['get_job_list']
        self.get_job_deps = conf['get_job_deps']
        self.get_data = conf['get_project_data']
        self.get_schedule = conf['get_schedule']
        self.jobs = {}
        self.job_confs = {}  # Map conf name to job name
        self.data = ProjectData(self.name)  # A set of related data
        self.schedule = self.get_schedule(self.schedule_paths)
        self.doc_path = PROJECT_REF + self.name + '/'
        self.mapping = {
            'name': self.name,
            'h1_underscore': '#' * len(self.name),
            'git_url': URL_GIT_BASE + self.name,
        }

    def find_jobs(self):
        for job_set_path in self.job_paths:
            for job_name, path in self.get_jobs(job_set_path).items():
                job = Job(job_name, path, self.name)
                job.find_deps(self.get_job_deps)
                job.schedule = self.schedule.get(job_name, '')
                self.jobs[job_name] = job

    # Find datasets and their input and output jobs
    def find_data(self):
        [self.get_data(self.jobs, self.data, data_path) for data_path in self.data_paths]
        self.data.add_data()    # Create Dataset objects

    def create_docs(self):
        print(f'Building project documentation in {self.doc_path}...')
        with open(PROJECT_REF_INDEX, 'a') as fd:
            fd.write(f'   {self.name}/{INDEX}\n')
        if not os.path.isdir(self.doc_path):
            os.mkdir(self.doc_path)
            create_file_by_template(TEMPLATE_PROJECT_INDEX, self.doc_path + INDEX, self.mapping)
        [self.jobs[name].create_doc(self.doc_path) for name in sorted(self.jobs)]
        self.data.create_docs()

    def draw_graphs(self):
        print(f'Drawing Job graphs for project {self.name}')
        [self.jobs[name].draw_graphs() for name in self.jobs]
        self.data.draw_graphs()

    def draw_workflows(self):
        # pp.pprint(self.schedule)
        pass
