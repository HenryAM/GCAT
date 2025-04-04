import tkinter as tk
from tkinter import ttk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import networkx as nx

class GUI(tk.Tk):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller

        self.geometry("800x600")

        # Create a vertical PanedWindow
        self.vertical_pane = tk.PanedWindow(self, orient=tk.HORIZONTAL, handlesize=20)
        self.vertical_pane.pack(fill=tk.BOTH, expand=True)

        # Create a horizontal PanedWindow for the bottom section
        self.horizontal_pane = tk.PanedWindow(self.vertical_pane, orient=tk.VERTICAL, handlesize=20)

        # Set up the window frames
        self.canvas_frame = self.CanvasFrame(self.vertical_pane, self.controller)  # Pass controller
        self.tool_frame = self.ToolFrame(self.horizontal_pane, self.controller)  # Pass controller
        self.info_frame = self.InfoFrame(self.horizontal_pane, self.controller)  # Pass controller

        # Add frames to the PanedWindows with minsize
        self.vertical_pane.add(self.canvas_frame, stretch="always", minsize=200)
        self.vertical_pane.add(self.horizontal_pane, stretch="always", minsize=200)

        self.horizontal_pane.add(self.info_frame, stretch="always", minsize=200)
        self.horizontal_pane.add(self.tool_frame, stretch="always", minsize=200)

    class CanvasFrame(ttk.Notebook):
        def __init__(self, root, controller):
            super().__init__(root)
            self.controller = controller  # Store the controller
            
            self.fig = Figure(figsize = (5,5), dpi = 100)
            self.ax = self.fig.add_subplot(111)
            self.ax.axis("off")
            self.canvas = FigureCanvasTkAgg(self.fig, master = self)
            self.widget = self.canvas.get_tk_widget()
            self.widget.pack(padx = (5,2), pady = 5, expand = True, fill = "both")
        
        def update_display(self):
            self.ax.clear()
            self.graph = self.controller.current_graph
            self.ax.axis("off")

            pos = nx.spring_layout(self.graph)
            nx.draw(self.graph, pos, ax=self.ax, with_labels=True)

            self.canvas.draw()


    class ToolFrame(ttk.Notebook):
        def __init__(self, root, controller):
            super().__init__(root)
            self.controller = controller  # Store the controller
            self.io_panel = ttk.Frame(self)  # Command line I/O
            self.tools_panel = ttk.Frame(self)  # Tool panel

            self.tools_panel.grid_columnconfigure(0, weight=0)
            self.tools_panel.grid_columnconfigure(1, weight=1)
            self.tools_panel.grid_columnconfigure(2, weight=0)

            # Place the tabs
            self.add(self.io_panel, text="I/O")
            self.add(self.tools_panel, text="Tools")

            self.input_line = tk.Entry(self.io_panel)
            self.output_line = tk.Text(self.io_panel)
            self.output_line.configure(state="disabled")

            self.input_line.pack(side=tk.BOTTOM, fill=tk.X, expand=False)
            self.output_line.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

            # Bind the Return key to send the command
            self.input_line.bind("<Return>", lambda event: self.send_command(self.input_line.get()))

            self.tools = {
                "add_graph": {
                    "title": "Add Graph",
                    "syntax": "add_graph <graph_name>",
                    "row": 0
                },
                "delete_graph": {
                    "title": "Delete Graph",
                    "syntax": "delete_graph <graph_name>",
                    "row": 1
                },
                "set_current": {
                    "title": "Set Current Graph",
                    "syntax": "set_current <graph_name>",
                    "row": 2
                },
                "add_edge": {
                    "title": "Add Edge",
                    "syntax": "add_edge <node1> <node2>",
                    "row": 3
                },
                "add_vertex": {
                    "title": "Add Vertex",
                    "syntax": "add_vertex <node>",
                    "row": 4
                },
                "delete_edge": {
                    "title": "Delete Edge",
                    "syntax": "delete_edge <node1> <node2>",
                    "row": 5
                },
                "delete_vertex": {
                    "title": "Delete Vertex",
                    "syntax": "delete_vertex <node>",
                    "row": 6
                }
            }

            self.entries = {}
            for tool_id, tool in self.tools.items():
                label = tk.Label(self.tools_panel, text = tool["title"])
                label.grid(row = tool["row"], column = 0, padx = 5, pady = 5)

                entry = tk.Entry(self.tools_panel)
                entry.grid(row = tool["row"], column = 1, padx = 5, pady = 5, stick = "ew")
                self.entries[tool_id] = entry

                entry.bind("<Return>", lambda event, t=tool_id, e=entry: self.send_command(f"{t} {e.get()}"))
                
                button = tk.Button(
                    self.tools_panel,
                    text = "→",
                    command=lambda t=tool_id, e=entry: self.send_command(f"{t} {e.get()}")
                )
                button.grid(row = tool["row"], column = 2, padx = 10, pady = 5, sticky = "ew")

        def log(self, arg):
            self.output_line.configure(state="normal")
            self.output_line.insert(tk.END, f"{arg}\n")
            self.output_line.configure(state="disabled")
        
        def clear(self):
            self.output_line.configure(state="normal")
            self.output_line.delete(1.0, tk.END)
            self.output_line.configure(state="disabled")

        def send_command(self, cmd, event=None):
            self.log(f">>> {cmd}")
            if cmd.strip():  # Check if the command is not empty
                try:
                    self.controller.process(cmd)  # Use the controller to process the command
                    self.input_line.delete(0, tk.END)  # Clear the input line
                    self.controller.process("refresh")
                except Exception as e:
                    self.log(f"Error: {e}")
            # Clear the entry field after processing the command
            for entry in self.entries.values():
                entry.delete(0, tk.END)

    class InfoFrame(ttk.Notebook):
        def __init__(self, root, controller):
            super().__init__(root)
            self.controller = controller  # Store the controller
            self.properties = ttk.Frame(self)
            self.graph_list = ttk.Frame(self)

            self.add(self.properties, text="Properties")
            self.add(self.graph_list, text="Graph List")

            self.properties_output = tk.Text(self.properties)
            self.properties_output.pack(anchor="center", expand=True, fill="both")
            self.properties_output.configure(state="disabled")

            self.update()

        def update(self):
            rowcount = 0
            for graph in self.controller.graph_list:
                label = tk.Label(self.graph_list, text = graph)
                label.grid(row = rowcount, column = 0, padx = 5, pady = 5)

                set_button = tk.Button(
                    self.graph_list,
                    text = "→",
                    command = lambda t = graph: self.controller.process(f"set_current {t}")
                )
                set_button.grid(row = rowcount, column = 1, padx = 10, pady = 5, sticky = "ew")

                rowcount += 1

        def log(self, arg):
            self.properties_output.configure(state="normal")
            self.properties_output.insert(tk.END, f"{arg}\n")
            self.properties_output.configure(state="disabled")
        
        def clear(self):
            self.properties_output.configure(state="normal")
            self.properties_output.delete(1.0, tk.END)
            self.properties_output.configure(state="disabled")
