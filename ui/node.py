"""
Copyright (c) 2024 laffra - All Rights Reserved. 

Represents a Node in the flow.
"""

import time

import ltk
from ui import connection


class Node(ltk.Model):
    """
    Represents the model for a node in a dataflow.
    """
    script: str = ""
    x: float = 100
    y: float = 2500

    def __init__(self, key="", script="", name="", secrets=None,
                packages=None, imports=None, inputs=None, selected=False,
                x=100, y=250, width="fit-content", height="fit-content",
                output="", output_type="", preview="", flow=None, **_args):
        super().__init__()
        self.key = key or f"{name}_{ltk.window.crypto.randomUUID()}"
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.script = script
        self.name = name
        self.flow = flow
        self.packages = packages
        self.secrets = secrets
        self.imports = imports
        self.inputs = inputs
        self.preview = preview
        self.output_type = output_type
        self.output = output
        self.selected = selected
        self.connections = {}

    def changed(self, name, value):
        """ Called when a node's value changes. """

    def get_script(self):
        """ Get the imports, script, and inputs for the node. """
        imports = [
            f"import {module}" for module in self.imports
        ]
        script = str(self.script)
        inputs = [
            f"{name}={connection.start_key}"
            for name, connection in self.connections.items()
        ]
        secrets = [
            f"os.environ['{name}'] = '{ltk.window.localStorage.getItem(name)}'"
            for name, prompt, url in self.secrets
        ]
        call = [
            f"{self.name}(",
            "    " + ",\n    ".join(inputs),
            ")"
        ]
        return "\n".join(imports + secrets + [script] + call)

    def evaluate(self):
        """ Evaluate the node. """
        if len(self.connections) < len(self.inputs):
            return
        try:
            script = self.get_script()
        except Exception: # pylint: disable=broad-exception-caught
            return False
        ltk.publish("Flow", "Worker", "run", [self.key, script])
        return True

    def save(self):
        """ Save the flow for this node. """


class NodeView(ltk.Div): # pylint: disable=too-many-public-methods
    """
    Represents a visual node view in dataflow, managing the display and behavior of a single node.
    """

    nodes = {}
    flow = None

    def __init__(self, model: Node, flow):
        super().__init__(
            ltk.Div()
                .addClass("node-view-progress"),
            ltk.Button("▶", self.run)
                .addClass("node-view-control")
                .addClass("node-view-run-button"),
            ltk.Button("✏️", self.edit)
                .addClass("node-view-control")
                .addClass("node-view-edit-button"),
            ltk.Button("❌", self.delete)
                .addClass("node-view-control")
                .addClass("node-view-delete-button"),
            ltk.Text(model.name)
                .on("click", ltk.proxy(lambda event: self.raise_to_top()))
                .addClass("node-view-label"),
            ltk.HBox(
                ltk.Div()
                    .addClass("node-view-inputs"),
                ltk.Div()
                    .addClass("node-view-spacer"),
                ltk.Div()
                    .addClass("node-view-outputs"),
            ).addClass("node-view-connectors"),
            ltk.Div(
                ltk.Div("")
                    .addClass("node-view-preview"),
                ltk.TextArea(str(model.script))
                    .on("change", ltk.proxy(lambda event: self.save_script()))
                    .addClass("node-view-editor"),
            ).addClass("node-view-content"),
        )
        self.flow = NodeView.flow = flow
        NodeView.nodes[model.key] = self
        self.model = model
        self.flow.model.nodes[model.key] = self.model

        self.addClass("node-view")
        if model.selected:
            self.addClass("node-view-selected")
        self.css(ltk.to_js({
            "left": f"{model.x}px",
            "top": f"{model.y}px",
            "width": model.width,
            "height": model.height,
            "min-height": max(30, 5 + len(model.inputs) * 20),
            "position": "absolute",
        }))
        self.attr("id", model.key)
        self.attr("key", model.key)

        self.add_connectors(model.output_type)
        self.input_connections = {}
        self.output_connections = []

        self.resizable(ltk.to_js({"handles": "se"}))
        self.draggable()
        self.on("drag", ltk.proxy(lambda ui, event: self.drag()))
        self.on("dragstop", ltk.proxy(lambda ui, event: self.dragstop()))
        self.on("resize", ltk.proxy(lambda ui, event: self.resize()))

        self.start_time = time.time()
        ltk.schedule(self.adjust_size, "adjust_size")

    def save_script(self):
        """ Save the script to the model """
        self.model.script = self.find(".node-view-editor").val()
        self.model.save()
        self.run()

    @classmethod
    def set_output(cls, key, output_connection):
        """ Set the output of a node """
        node = cls.nodes[key]
        node.output_connections.append(output_connection)

    @classmethod
    def set_input(cls, key, name, input_connection):
        """ Set the input of a node """
        node = cls.nodes[key]
        node.input_connections[name] = input_connection
        node.model.connections[name] = input_connection.model

    def run(self, _event=None):
        """ Run this node """
        self.evaluate()

    def edit(self, _event):
        """ Edit this node """
        self.find(".node-view-editor").addClass("node-view-editor-active")

    def delete(self, _event):
        """ Delete this node """
        self.flow.delete_node(self)
        self.model.save()

    def raise_to_top(self):
        """ Raise the node to the top """
        self.appendTo(ltk.find(".flow"))

    def drag(self):
        """ The user is dragging the node """
        connection.ConnectionView.draw_all()

    def dragstop(self):
        """ The user dragged the node """
        self.model.x = ltk.window.parseFloat(self.css("left"))
        self.model.y = ltk.window.parseFloat(self.css("top"))
        self.model.save()
        connection.ConnectionView.draw_all()

    def resize(self):
        """ The user resize the node """
        self.model.width = self.width()
        self.model.height = self.height()
        self.model.save()
        connection.ConnectionView.draw_all()

    def add_connectors(self, output_name):
        """ Add input and output connectors """
        for name, type_name in self.model.inputs:
            self.find(".node-view-inputs").append(
                connection.InputConnector(name, type_name, self)
                    .addClass("node-view-connector")
                    .addClass("node-view-input")
            )
        if output_name != "None":
            self.find(".node-view-outputs").append(
                connection.OutputConnector(output_name, output_name, self)
                    .addClass("node-view-connector")
                    .addClass("node-view-output")
            )
        if not self.model.inputs:
            self.find(".node-view-progress").remove()
    
    def adjust_size(self):
        """ Adjust the size of the node """
        self.css("width", sum([
            self.find(".node-view-inputs").width(),
            self.find(".node-view-outputs").width(),
            50,
        ]))
        print("set width",
            self.find(".node-view-inputs").width(),
            self.find(".node-view-outputs").width(),
        )

    def start_running(self):
        """ Start the running node """
        self.removeClass("node-view-error")
        self.addClass("node-view-running")
        self.start_time = time.time()

    def stop_running(self):
        """ Stop the running node """
        self.removeClass("node-view-running")
        duration = time.time() - self.start_time
        info = f"{self.model.name} | {duration:.2f}s" if self.model.inputs else self.model.output
        self.find(".node-view-label").text(info)
        connection.ConnectionView.draw_all()

    def evaluate(self):
        """ Evaluate the node. """
        if self.model.evaluate():
            self.start_running()

    def handle_worker_result(self, flow, result):
        """
        Handles the result from the worker, updating the UI.
        """
        key = result["key"]
        node = NodeView.nodes[key]
        node.stop_running()
        model = node.model
        model.preview = preview = result["preview"]
        if result.get("error"):
            ltk.find(f"#{key}").addClass("node-view-error")
            preview = f"Error: <pre>{result['error']}</pre>"
        if preview.startswith("<"):
            node.find(".node-view-preview").empty().append(
                ltk.create(preview)
            )
        else:
            node.find(".node-view-label").text(preview)
        if not result.get("error"):
            for line in flow.connections:
                if line.start_key == key:
                    NodeView.nodes[line.end_key].evaluate()
