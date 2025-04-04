import gui
import controller

if __name__ == "__main__":
    controller = controller.Controller()
    gui = gui.GUI(controller)
    controller.set_gui(gui)
    gui.mainloop()