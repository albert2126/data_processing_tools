import os
from graphviz import Digraph
import pprint

from utils import create_file_by_template, read_json_schema, replace_suffix
from globals import DATA_REF, DATA_REF_INDEX, INDEX, PROJECT_REF, GRAPH_FILE_SUFFIX, TEMPLATE_DATA, \
    TEMPLATE_PROJECT_DATA, HMS_DATABASE_INPUT, HMS_DATABASE_OUTPUT, HMS_BASE_URL, INCLUSIONS_DATA

pp = pprint.PrettyPrinter(indent=2)


# An output of a job:
class DataSet:
    def __init__(self, name, connections, parent):
        self.name = name
        self.connections = connections  # {"input": job, "output":[jobs]}
        self.inputs = {}    # {ds1:{}, ds2{ds21:{}, ds22:{ds221:{}, ds222{}}}}
        self.outputs = {}    # {ds1:{}, ds2{ds21:{}, ds22:{ds221:{}, ds222{}}}}
        self.parent = parent    # A group of datasets for a specific project
        self.project_name = parent.name
        self.project_doc_path = PROJECT_REF + self.project_name + '/'
        self.doc_folder = DATA_REF + self.project_name + '/'
        self.doc_path = self.doc_folder + self.name + '.rst'
        self.graph_name = self.name + GRAPH_FILE_SUFFIX
        self.lineage_name = self.name + '_lineage' + GRAPH_FILE_SUFFIX

    def add_schema(self):
        schema = read_json_schema(self.name)
        if schema and len(schema[1]) > 0:
            prim_key, columns = schema
            with open(self.doc_path, 'a') as fd:
                fd.write('**Schema**\n\n')
                fd.write(f'Primary key: {prim_key}\n\n')
                fd.write('.. list-table::\n')
                fd.write('   :widths: 1 1 3\n')
                fd.write('   :header-rows: 1\n')
                fd.write('   :stub-columns: 1\n\n')
                fd.write('   *   -   Name\n')
                fd.write('       -   Type\n')
                fd.write('       -   Description\n')
                for col in columns:
                    fd.write(f'   *   -   ' + replace_suffix(col['name'], '_', r'\_') + '\n')
                    fd.write(f'       -   {col["type"]}\n')
                    fd.write(f'       -   \n')
                fd.write('\n')

    def create_doc(self):
        with open(DATA_REF + self.project_name + '/index.rst', 'a') as fd:
            fd.write(f'   {self.name}\n')
        database = HMS_DATABASE_OUTPUT if 'input_job' in self.connections else HMS_DATABASE_INPUT
        hms_url = HMS_BASE_URL % {'db': database, 'table': self.name}
        inclusion = f'../inclusions/{self.name}.txt' if self.name in INCLUSIONS_DATA \
            else '../inclusions/empty.txt'
        mapping = {
            'name': self.name,
            'h1_underscore': '#' * len(self.name),
            'project': self.project_name,
            'filename': self.name + GRAPH_FILE_SUFFIX + '.svg',
            'lineage_filename': self.name + '_lineage' + GRAPH_FILE_SUFFIX + '.svg',
            'hms_url': hms_url,
            'inclusion': inclusion,
        }
        create_file_by_template(TEMPLATE_DATA, self.doc_path, mapping)
        self.add_schema()

    def draw_graph(self):
        dot = Digraph(
            filename=self.graph_name,
            format='svg',
            comment=f'Dataset flow for {self.name}',
            graph_attr={'rankdir': 'LR'},
            node_attr={'style': 'filled', 'width': '3'}
        )
        # Draw nodes and edges:
        dot.node(
            self.name,
            shape='folder',
            color='darkorange4',
            fillcolor='darkorange4',
            fontcolor='white',
        )
        if 'input_job' in self.connections:
            jnode = self.connections['input_job'].name
            dot.node(
                jnode,
                shape='cds',
                color='cadetblue2',
                fillcolor='cadetblue1',
                href='../../../projects/' + self.project_name + '/' + jnode + '/',
                target='_top',
            )
            dot.edge(jnode, self.name)
        if 'output_jobs' in self.connections:
            for job in self.connections['output_jobs']:
                jnode = job.name
                dot.node(
                    jnode,
                    shape='cds',
                    color='cadetblue2',
                    fillcolor='cadetblue1',
                    href='../../../projects/' + self.project_name + '/' + jnode + '/',
                    target='_top',
                )
                dot.edge(self.name, jnode)
        dot.render(directory=self.doc_folder)
        os.remove(self.doc_folder + self.graph_name)

    def input_connections(self, inputs, dataset, passed_jobs, dot, dest):
        # If this is an ingested dataset or its job was already processed:
        if 'input_job' not in dataset.connections or dataset.connections['input_job'].name in passed_jobs:
            return
        job = dataset.connections['input_job']
        passed_jobs.append(job.name)
        for ds in job.input:
            dot.node(
                ds,
                href=f'../{ds}/',
                target='_top',
            )
            dot.edge(ds, dest)
            inputs.setdefault(ds, {})
            # Recursive call:
            self.parent.ds[ds].input_connections(inputs[ds], self.parent.ds[ds], passed_jobs, dot, ds)

    def output_connections(self, outputs, dataset, passed_jobs, dot, src):
        if 'output_jobs' not in dataset.connections:
            return
        output_jobs = dataset.connections['output_jobs']
        for job in output_jobs:
            if job.name in passed_jobs:
                return
            passed_jobs.append(job.name)
            for ds in job.output:
                dot.node(
                    ds,
                    href=f'../{ds}/',
                    target='_top',
                )
                dot.edge(src, ds)
                outputs.setdefault(ds, {})
                # Recursive call
                self.parent.ds[ds].output_connections(outputs[ds], self.parent.ds[ds], passed_jobs, dot, ds)

    def draw_lineage(self):
        dot = Digraph(
            filename=self.lineage_name,
            format='svg',
            graph_attr={'rankdir': 'LR'},
            node_attr={'style': 'filled', 'width': '3', 'shape': 'folder', 'color': 'cornsilk3',
                       'fillcolor': 'cornsilk'}
        )
        dot.node(
            self.name,
            shape='folder',
            color='darkorange4',
            fillcolor='darkorange4',
            fontcolor='white',
        )
        self.input_connections(self.inputs, self, [], dot, self.name)
        self.output_connections(self.outputs, self, [], dot, self.name)
        dot.render(directory=self.doc_folder)
        # os.remove(self.doc_folder + self.graph_name)


# A set of data of a particular project:
class ProjectData:
    def __init__(self, name):
        self.name = name    # Project name
        self.data = {}      # Dataset name to input and output job objects mapping
        self.ds = {}        # Dataset name to dataset objects mapping
        self.doc_path = DATA_REF + self.name + '/'
        self.mapping = {
            'name': self.name,
            'h1_underscore': '#' * len(self.name),
        }

    # Create DataSet objects:
    def add_data(self):
        [self.ds.setdefault(ds_name, DataSet(ds_name, self.data[ds_name], self)) for ds_name in self.data]

    def create_docs(self):
        # print(f'Building data documentation in {self.doc_path}...')
        with open(DATA_REF_INDEX, 'a') as fd:
            fd.write(f'   {self.name}/{INDEX}\n')
        if not os.path.isdir(self.doc_path):
            os.mkdir(self.doc_path)
            create_file_by_template(TEMPLATE_PROJECT_DATA, self.doc_path + INDEX, self.mapping)
        [self.ds[name].create_doc() for name in sorted(self.ds)]

    def draw_graphs(self):
        print(f'Drawing Dataset graphs for project {self.name}')
        [self.ds[name].draw_graph() for name in self.ds]
        for ds in self.ds.values():
            ds.draw_lineage()
