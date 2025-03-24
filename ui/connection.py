"""
Copyright (c) 2024 laffra - All Rights Reserved. 

Represents a connection between two nodes in a dataflow.
"""

import json

import ltk

class Connection():
    """
    A connection between two nodes in a dataflow.
    """
    def __init__(self, start_key: str, end_key: str, name: str, flow=None):
        self.start_key = start_key
        self.end_key = end_key
        self.name = name
        self.flow = flow


class ConnectionView():
    """
    A connection between two nodes in a dataflow.
    """

    current = None
    connections = []

    def __init__(self, model, reverse=False):
        from ui import node # pylint: disable=import-outside-toplevel
        self.model = model
        node = node.NodeView.nodes[model.start_key]
        self.start = node.find(f".node-view-input[name='{model.name}']") \
                if reverse else \
                node.find(".node-view-output")
        self.end = (
            node.NodeView.nodes[model.end_key] \
                .find(f".node-view-input[name='{model.name}']")
            if model.end_key else
            ltk.Div()
                .addClass("node-view-temporary")
                .css("left", self.start.offset().left)
                .css("top", self.start.offset().top)
                .append(
                    ltk.Text("●")
                        .addClass("connector-dot")
                )
                .appendTo(ltk.find(".flow"))
        )
        self.line = None
        self.draw()

    def connect(self, connector, _event):
        """ Complete the connection to the second connector. """
        from ui import node # pylint: disable=import-outside-toplevel
        self.end.remove()
        self.end = connector.element
        self.draw()
        self.model.end_key = self.end.attr("key")
        self.flip_if_needed()
        self.remove_old_connection()
        ConnectionView.connections.append(self)
        node.NodeView.flow.model.add_connection(self.model)
        self.add_to_nodes()
        self.model.name = self.end.attr("name")
        ConnectionView.current = None
        node.NodeView.nodes[self.start.attr("key")].evaluate()

    def remove_old_connection(self):
        """ Remove the old connections from the nodes. """
        for connection in ConnectionView.connections:
            if connection.model.end_key != self.model.end_key:
                continue
            if connection.model.name != self.model.name:
                continue
            connection.line.remove()

    def flip_if_needed(self):
        """ Flip the connection if it's backwards. """
        if self.end.hasClass("node-view-output"):
            self.end, self.start = self.start, self.end
            self.model.start_key = self.start.attr("key")
            self.model.end_key = self.end.attr("key")
            self.model.name = self.end.attr("name")
            self.draw()

    def draw(self):
        """ Draw the connection as an arrow between the two connectors. """
        if self.line:
            self.line.remove()
        self.line = ltk.window.LeaderLine.new(
            self.start.find(".connector-dot")[0],
            self.end.find(".connector-dot")[0],
            ltk.to_js({
                "color": "#1f51b540",
                "endPlug": "behind",
                "size": 5,
            })
        )

    @classmethod
    def draw_all(cls):
        """ Draw all the connections """
        for connection in cls.connections:
            try:
                connection.draw()
            except: # pylint: disable=bare-except
                pass

    @classmethod
    def click(cls, connector, event):
        """ Handle the click event on a connector. """
        from ui import node # pylint: disable=import-outside-toplevel
        if cls.current:
            cls.current.connect(connector, event)
            clear()
        else:
            model = Connection(
                connector.attr("key"),
                "",
                connector.attr("name"),
                node.NodeView.flow.model
            )
            cls.current = cls(model, connector.hasClass("node-view-input"))

    @classmethod
    def mousemove(cls, event):
        """ Handle the mouse move event.  """
        if cls.current:
            cls.current.end \
                .css("left", event.clientX) \
                .css("top", event.clientY)
            cls.current.draw()

    @classmethod
    def clear(cls):
        """ Clear the current connection. """
        if cls.current:
            cls.current.line.remove()
        if cls.current in cls.connections:
            cls.connections.remove(cls.current)
        cls.current = None

    def add_to_nodes(self):
        """ Add this connection to the start and end nodes. """
        from ui import node # pylint: disable=import-outside-toplevel
        node.NodeView.set_output(self.start.attr("key"), self)
        node.NodeView.set_input(self.end.attr("key"), self.end.attr("name"), self)


class Connector(ltk.Div):
    """
    Represents an input/output connector in a node view.
    """
    def __init__(self, name, type_name, node):
        super().__init__()
        self.name = name
        self.node = node
        self.type_name = type_name
        self.on("click", ltk.proxy(self.click))
        self.attr("key", node.model.key)
        self.attr("name", name)
        self.attr("type_name", type_name)
        nodes = [
            ltk.Text("●")
                .addClass("connector-dot"),
            ltk.Text(name)
                .addClass("connector-label"),
        ]
        self.append(nodes if self.kind() == "input" else list(reversed(nodes)))

    def click(self, event):
        """ Click the input/output connector. """
        event.stopPropagation()
        self.highlight_compatible_nodes()
        self.highlight_compatible_options()
        ConnectionView.click(self, event)

    def highlight_compatible_nodes(self):
        """ Highlight the compatible nodes for this connector. """
        opposite_kind = "output" if self.kind() == "input" else "input"
        ltk.find(f".node-view-{opposite_kind}") \
            .filter(lambda _index, element: ltk.find(element).attr("type_name") == self.type_name) \
            .addClass("matching-connector")

    def highlight_compatible_options(self):
        """ Highlight the compatible options for this connector. """
        kind = self.kind()
        type_name = self.type_name

        def match(_index, element):
            option = ltk.find(element)
            if kind == "output":
                input_types = [typename for name, typename in json.loads(option.attr("inputs"))]
                return type_name in input_types
            else:
                return type_name == option.attr("output")

        ltk.find(".node-option") \
            .filter(match) \
            .addClass("matching-option")

    def kind(self):
        """ The kind of connector. """
        raise NotImplementedError()


class OutputConnector(Connector):
    """
    Represents an output connector in a node view.
    """
    def kind(self):
        """ The kind of connector. """
        return "output"


class InputConnector(Connector):
    """
    Represents an input connector in a node view.
    """
    def kind(self):
        """ The kind of connector. """
        return "input"



def clear():
    """ Remove the highlights from all nodes and options. """
    ltk.find(".matching-connector").removeClass("matching-connector")
    ltk.find(".matching-option").removeClass("matching-option")
    ConnectionView.clear()


ltk.find(".flow") \
    .on("click", ltk.proxy(lambda event: ltk.schedule(clear, "clear"))) \
    .on("mousemove", ltk.proxy(ConnectionView.mousemove))
