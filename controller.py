import networkx as nx
import matplotlib.pyplot as plt

class Controller():
    '''
        Logic Controller for GCAT v0.09. This will receive input via user interactions with gui,
        send commands to the graph object, receive data, and send back to gui. 
    '''
    def __init__(self):
        self.debug = False
        self.gui = None
        self.graph_list = {"default": nx.Graph()}
        self.current_graph = self.graph_list["default"]
        self.set_current("default")
        self.data = {
            "vertex_count": lambda: len(self.current_graph.nodes()),
            "vertex_list": lambda: list(self.current_graph.nodes()),
            "edge_count": lambda: len(self.current_graph.edges()),
            "edge_list": lambda: list(self.current_graph.edges()),
            "degree_list": lambda: list(self.current_graph.degree()),
            "spectrum": lambda: [round(abs(float(val).real), 3) for val in nx.spectrum.laplacian_spectrum(self.current_graph)],
            "density": lambda: nx.density(self.current_graph),
            "diameter": lambda: nx.diameter(self.current_graph),
            "radius": lambda: nx.radius(self.current_graph)
        }

    def set_gui(self, gui):
        self.gui = gui

    def add_graph(self, graph_name):
        print(f"Attempting to add graph: {graph_name}")
        if graph_name in self.graph_list:
            print(f"Graph '{graph_name}' already exists.")
            return
        self.graph_list[graph_name] = nx.Graph()
        self.set_current(graph_name)
        print(f"Graph '{graph_name}' added.")
        print(self.graph_list)

    def delete_graph(self, graph_name):
        if self.current_graph == self.graph_list.get(graph_name):
            self.set_current("default")
        self.graph_list.pop(graph_name, None)

    def set_current(self, graph_name):
        if graph_name in self.graph_list:
            self.current_graph = self.graph_list[graph_name]
            try:
                self.process("refresh")
            except Exception:
                pass
        else:
            print(f"Graph '{graph_name}' does not exist.")

    def show_graph(self):
        if self.current_graph:
            self.gui.canvas_frame.update_display()
        else:
            self.gui.tool_frame.log("No current graph to display.")
        
    def flip_debug(self):
        if self.debug:
            self.debug = False
        else:
            self.debug = True

    def add_data(self):
        self.gui.info_frame.clear()
        for key, value in self.data.items():
            try:
                self.gui.info_frame.log(f"{key}: {value()}")
            except Exception as e:
                self.gui.info_frame.log(f"{key}: Error: {e}")

    def refresh(self):
        self.gui.info_frame.update()
        self.process("log_data")
        self.process("show_graph")

    def process(self, cmd):
        command, *args = cmd.split()
        command_list = {
            "add_graph": self.add_graph,
            "delete_graph": self.delete_graph,
            "set_current": self.set_current,
            "add_edge": lambda *args: self.current_graph.add_edge(*args),
            "add_vertex": lambda *args: self.current_graph.add_node(*args),
            "delete_edge": lambda *args: self.current_graph.remove_edge(*args),
            "delete_vertex": lambda *args: self.current_graph.remove_node(*args),
            "show_graph": self.show_graph,
            "debug": self.flip_debug,
            "log_data": self.add_data,
            "refresh": self.refresh
        }
        if self.debug:
            self.gui.tool_frame.log(f"DEBUG: {cmd}")
        if command in command_list:
            command_list[command](*args)
        else:
            self.gui.tool_frame.log(f"Unknown command: {command}")