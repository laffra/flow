"""
Copyright (c) 2024 laffra - All Rights Reserved. 

The FlowView class is responsible for rendering and managing the dataflow user interface.
It handles user interactions, such as node selection, editing, and navigation, as well as
integrating with the underlying flow model.
"""

import json

import ltk

from polyscript import XWorker # type: ignore   pylint: disable=import-error

from ui import connection
from ui import node


class Flow(ltk.Model):  # pylint: disable=too-many-instance-attributes
    """
    A class representing a data flow.
    
    The `Flow` class is a subclass of the `Model` class and provides functionality
    for managing a dependency graph and executing data transformations.
    """
    def __init__(self, uid="", name="Untitled Flow",    # pylint: disable=too-many-arguments
                 nodes=None, screenshot="/flow.png",
                 created_timestamp=0, updated_timestamp=0,
                 packages="",
                 connections=None,
                 new=False,
                 _class="Flow", _="Flow"):
        super().__init__()
        self.uid = uid
        self.name = name
        self.screenshot = screenshot
        self.nodes = nodes or {}
        self.connections = connections or []
        self.created_timestamp = created_timestamp
        self.updated_timestamp = updated_timestamp
        self.packages = packages
        self.new = new
        print("Create flow", [type(connection) for connection in self.connections])

    def add_connection(self, new_connection):
        """
        Adds a connection to the flow.
        """
        self.connections = [
            c
            for c in self.connections
            if c.end_key != new_connection.end_key and c.name != new_connection.name
        ] + [new_connection]

    def save(self):
        """ Save this flow and all the nodes. """



class FlowView():
    """
    The FlowView class is responsible for managing the user interface and interactions of a
    dataflow application. It handles the rendering of the nodes, selection and
    navigation, and integration with the underlying dataflow model.
    """
    def __init__(self, model: Flow):
        self.model = model
        self.secrets = {}
        self.load_nodes()
        self.load_connections()

    def load_nodes(self):
        """ Load the nodes that were saved in this flow. """
        for key, flow_node in list(self.model.nodes.items()):
            if not isinstance( flow_node, dict):
                continue
            self.model.nodes[key] = self.create_node(** flow_node).model

    def delete_node(self, node_view):
        """ Delete a node from the flow. """
        node_view.remove()
        if node_view.model.key in self.model.nodes:
            del self.model.nodes[node_view.model.key]
        connection.ConnectionView.draw_all()

    def load_connections(self):
        """ Load the connections that were saved in this flow. """
        if self.model.connections and not isinstance(self.model.connections[0], dict):
            return
        self.model.connections = list(filter(None, [
            self.create_connection(**connection)
            for connection in self.model.connections
        ]))

    def handle_worker_result(self, result):
        """
        Handles the result from the worker, updating the UI.
        """
        key = result["key"]
        model = self.model.nodes[key]
        model.output = result["value"]
        if result.get("error"):
            ltk.find(f"#{key}").addClass("node-view-error")
            result["preview"] = f"<pre>{result['error']}</pre>"
        model.preview = result["preview"]
        ltk.find(f"#{key}").find(".node-view-preview").empty().append(
            ltk.create(model.preview)
            if model.preview.startswith("<") else
            ltk.Preformatted(model.preview)
        )
        node.NodeView.nodes[key].stop_running()
        for line in self.model.connections:
            if line.start_key == key:
                node.NodeView.nodes[line.end_key].evaluate()

    def worker_ready(self, _info):
        """
        Evaluate nodes that need running in the worker.
        """
        for root in [ node for node in self.model.nodes.values() if not node.inputs ]:
            node.NodeView.nodes[root.key].evaluate()

    def create_connection(self, start_key, end_key, name):
        """ Create a new connection """
        try:
            model = connection.Connection(start_key, end_key, name, self.model)
            view = connection.ConnectionView(model)
            return view.model
        except: # pylint: disable=bare-except
            import traceback # pylint: disable=import-outside-toplevel
            traceback.print_exc()

    def create_node(self, category="", packages="", imports=None, script="", name="",
                            secrets=None, output="", output_type="", inputs=None, **kwargs):
        """ Create a new node """
        print("create_node", inputs)
        model = node.Node(
            key=f"{name}_{len(node.NodeView.nodes)}",
            flow=self.model, category=category, name=name,
            secrets=secrets, packages=packages, imports=imports, script=script,
            output=output, output_type=output_type, inputs=inputs.copy(),
            **kwargs
        )
        self.check_secrets(secrets)
        view = node.NodeView(model, self)
        view.appendTo(ltk.find(".flow"))
        return view

    def check_secrets(self, secrets):
        """ Check if any secrets need to be entered """
        for key, prompt, url in secrets:
            self.secrets[key] = url
            if not ltk.window.localStorage.getItem(key):
                ltk.window.localStorage.setItem(
                    key,
                    ltk.window.prompt(
                        f"{prompt}. See {url} for more information."
                    )
                )

    def create_option(self, parent,
            category="", name="", packages=None, imports=None, inputs=None,
            secrets=None, output_type="", script=""):
        """ Add a node option """
        parent.append(
            ltk.Button(
                name,
                lambda event: self.create_node(
                    category=category, name=name, packages=packages, imports=imports,
                    secrets=secrets, inputs=inputs, output_type=output_type, script=script
                )
            )
            .addClass("node-option")
            .attr("inputs", json.dumps(inputs))
            .attr("output", output_type)
        )

flow = FlowView(Flow())

def worker_ready(data):
    """ Worker is ready """
    print(data)

def handle_error(data):
    """ Worker errored """
    print("###### Error", data)
    handle_result(data)

def handle_result(data):
    """ Worker ran a node """
    key, preview = ltk.to_py(data)
    flow_node = node.NodeView.nodes[key]
    flow_node.handle_worker_result(flow.model, {
        "key": key,
        "preview": preview,
    })

def handle_options(options):
    """ Worker found node options """
    ltk.find(".node-options").empty()
    for name, options in ltk.to_py(options).items():
        category = ltk.VBox(ltk.Text(name)).addClass("node-option-category")
        ltk.find(".node-options").append(category)
        for option in options:
            flow.create_option(category, **option)

def setup_worker():
    """ Setup the worker """
    ltk.subscribe("Main", "ready", worker_ready)
    ltk.subscribe("Main", "result", handle_result)
    ltk.subscribe("Main", "error", handle_error)
    config = {
        "interpreter": "pyodide/pyodide.js",
        "packages": [ 
            "pandas", "duckdb", "matplotlib", "plotly", "fmpsdk",
        ],
        "files": { },
    }
    worker = XWorker("worker/runner.py", config=ltk.to_js(config), service_worker=True, type="pyodide")
    ltk.register_worker("pyodide-runner", worker)


def setup_options():
    """ Setup the options """
    config = {
        "interpreter": "pyodide/pyodide.js",
        "packages": [],
        "files": {
            "worker/options.py": "worker/options.py",
            "flows/__init__.py": "flows/__init__.py",
            "flows/basic/boolean.py": "flows/basic/boolean.py",
            "flows/basic/string.py": "flows/basic/string.py",
            "flows/charts/plot.py": "flows/charts/plot.py",
            "flows/finance/fmp.py": "flows/finance/fmp.py",
            "flows/data/sql.py": "flows/data/sql.py",
            "flows/input/file.py": "flows/input/file.py",
        },
    }
    ltk.subscribe("Main", "options", handle_options)
    options = XWorker("worker/options.py", config=ltk.to_js(config), service_worker=True, type="pyodide")
    ltk.register_worker("pyodide-options", options)

def setup():
    """ Setup the flow """
    setup_options()
    setup_worker()
