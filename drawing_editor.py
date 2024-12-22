import tkinter as tk
from tkinter import simpledialog, colorchooser, messagebox, filedialog
import sys
import xml.etree.ElementTree as ET


class EditDialog(simpledialog.Dialog):
    def __init__(self, parent, title, initial_color="black", is_line=True):
        self.is_line = is_line
        self.initial_color = initial_color
        super().__init__(parent, title)
        
    def body(self, master):
        tk.Label(master, text="Choose color:").grid(row=0, column=0)
        self.color_var = tk.StringVar(value=self.initial_color)
        colors = ["black", "red", "green", "blue"]
        self.color_menu = tk.OptionMenu(master, self.color_var, *colors)
        self.color_menu.grid(row=0, column=1)

        if not self.is_line:
            tk.Label(master, text="Corner style:").grid(row=1, column=0)
            self.corner_var = tk.StringVar(value="square")
            tk.Radiobutton(master, text="Square", variable=self.corner_var, value="square").grid(row=1, column=1)
            tk.Radiobutton(master, text="Rounded", variable=self.corner_var, value="round").grid(row=1, column=2)

        return self.color_menu  # initial focus

    def apply(self):
        self.result = self.color_var.get(), self.corner_var.get() if not self.is_line else "square"

def edit_properties(parent, initial_color="black", is_line=True):
    dialog = EditDialog(parent, "Edit Properties", initial_color, is_line)
    return dialog.result if dialog.result else (initial_color, "square")

class PropertyDialog(simpledialog.Dialog):
    def __init__(self, parent, title, initial_color="black", is_line=True):
        self.is_line = is_line
        self.color = initial_color
        self.corner_style = tk.StringVar(value="square")
        super().__init__(parent, title)
        
    def body(self, master):
        tk.Label(master, text="Color:").grid(row=0)
        self.color_button = tk.Button(master, bg=self.color, command=self.choose_color)
        self.color_button.grid(row=0, column=1)

        if not self.is_line:
            tk.Label(master, text="Corner Style:").grid(row=1)
            tk.Radiobutton(master, text="Square", variable=self.corner_style, value="square").grid(row=1, column=1)
            tk.Radiobutton(master, text="Rounded", variable=self.corner_style, value="round").grid(row=1, column=2)
        return self.color_button

    def choose_color(self):
        color, _ = colorchooser.askcolor(initialcolor=self.color)
        if color:
            self.color = color
            self.color_button.config(bg=color)

    def apply(self):
        # This method will be called automatically to process the data
        pass  # We handle the changes directly in the dialog callbacks

class DrawingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Advanced Drawing Editor")

        self.canvas = tk.Canvas(root, width=800, height=600, bg='white')
        self.canvas.pack(expand=tk.YES, fill=tk.BOTH)

        self.selected_tool = None
        self.current_object = None
        self.last_object = None
        self.objects = {}
        self.object_id = 1
        self.operation_mode = None
        self.groups = {}  # Dictionary to store group information
        self.group_id_counter = 0  # Counter to assign unique IDs to each group
        self.selected_objects = set() 
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.is_saved = True
        self.setup_menus()
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def setup_menus(self):
        menu_bar = tk.Menu(self.root)
        
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="Exit", command=self.root.quit)
        menu_bar.add_cascade(label="File", menu=file_menu)

        draw_menu = tk.Menu(menu_bar, tearoff=0)
        tools = ["line", "rectangle", "select", "edit"]
        for tool in tools:
            draw_menu.add_command(label=tool.capitalize(), command=lambda t=tool: self.select_tool(t))
        menu_bar.add_cascade(label="Draw/Edit", menu=draw_menu)

        edit_menu = tk.Menu(menu_bar, tearoff=0)
        edit_menu.add_command(label="Delete", command=lambda: self.set_operation_mode("delete"))
        edit_menu.add_command(label="Copy", command=lambda: self.set_operation_mode("copy"))
        menu_bar.add_cascade(label="Tools", menu=edit_menu)

        group_menu = tk.Menu(menu_bar, tearoff=0)
        group_menu.add_command(label="Group", command=self.create_group)
        group_menu.add_command(label="Ungroup", command=self.ungroup_selected_group)
        menu_bar.add_cascade(label="Group", menu=group_menu)
        
        file_menu.add_command(label="Open", command=self.open_file)
        file_menu.add_command(label="Save", command=self.save_file)
        file_menu.add_command(label="Export to XML", command=self.export_to_xml)

        # file_menu.add_separator()
        # file_menu.add_command(label="Exit", command=self.root.quit)
        # menu_bar.add_cascade(label="File", menu=file_menu)

        self.root.config(menu=menu_bar)

    def clear_selections(self):
        """Clear all selections."""
        for obj in self.selected_objects:
            self.canvas.itemconfig(obj, outline='black')  # Reset outline
        self.selected_objects.clear()
    def on_canvas_click(self, event):
        # Output the event state to debug
        self.is_saved = False
        # print("Event state:", event.state)  # Check what the state prints
        ctrl_pressed = (event.state & 0x08) != 0
        # print("Ctrl pressed:", ctrl_pressed)

        obj_id_tuple = self.canvas.find_closest(event.x, event.y, halo=10)
        if obj_id_tuple:
            obj_id = obj_id_tuple[0]
            print("Object clicked:", obj_id)  # Check which object is clicked
            if not ctrl_pressed:
                if obj_id in self.selected_objects:
                    self.selected_objects.remove(obj_id)
                    self.canvas.itemconfig(obj_id, outline='black')
                    print("Object deselected:", obj_id)
                else:
                    self.selected_objects.add(obj_id)
                    self.canvas.itemconfig(obj_id, outline='red')
                    print("Object selected:", obj_id)
            else:
                self.clear_selections()
                self.selected_objects.add(obj_id)
                self.canvas.itemconfig(obj_id, outline='red')
                print("New selection:", obj_id)
        # self.is_saved = False



    def select_tool(self, tool):
        self.selected_tool = tool
        if tool == "edit":
            self.operation_mode = "edit"
        else:
            self.operation_mode = None
        if self.last_object:
            self.reset_highlight(self.last_object)
        self.current_object = None
        self.canvas.unbind("<Button-1>")
        self.canvas.unbind("<B1-Motion>")
        self.canvas.unbind("<ButtonRelease-1>")
        if tool == "select" or tool == "edit":
            self.canvas.bind("<Button-1>", self.select_object)
        else:
            self.canvas.bind("<Button-1>", self.start_draw)
            self.canvas.bind("<B1-Motion>", self.on_draw)
            self.canvas.bind("<ButtonRelease-1>", self.stop_draw)

    def set_operation_mode(self, mode):
        self.operation_mode = mode
        self.canvas.bind("<Button-1>", self.perform_operation)

    def perform_operation(self, event):
        selected_object = self.canvas.find_closest(event.x, event.y, halo=10)[0]
        if self.operation_mode == "delete":
            self.canvas.delete(selected_object)
            del self.objects[selected_object]
        elif self.operation_mode == "copy":
            self.copy_object(selected_object)
        self.operation_mode = None

    def delete_object(self, event):
        selected_object = self.canvas.find_closest(event.x, event.y, halo=10)[0]
        self.canvas.delete(selected_object)
        del self.objects[selected_object]

    def copy_object(self, event):
        selected_object = self.canvas.find_closest(event.x, event.y, halo=10)[0]
        self.copy_object(selected_object)
    def start_draw(self, event):
        self.start_x = event.x
        self.start_y = event.y
        options = {'tags': str(self.object_id)}
        if self.selected_tool == "line":
            options['fill'] = 'black'
            self.current_object = self.canvas.create_line(self.start_x, self.start_y, event.x, event.y, **options)
        elif self.selected_tool == "rectangle":
            options['outline'] = 'black'
            self.current_object = self.canvas.create_rectangle(self.start_x, self.start_y, event.x, event.y, **options)
        self.objects[self.current_object] = {'type': self.selected_tool, 'coordinates': (self.start_x, self.start_y, event.x, event.y)}

    def on_draw(self, event):
        self.is_saved = False
        if self.current_object:
            self.canvas.coords(self.current_object, self.start_x, self.start_y, event.x, event.y)

    def stop_draw(self, event):
        self.current_object = None

    def prepare_to_move_object(self, event):
        if self.last_object:
            self.reset_highlight(self.last_object)
        self.current_object = self.canvas.find_closest(event.x, event.y, halo=10)[0]
        object_type = self.canvas.type(self.current_object)
        
        # Handling visual feedback based on object type
        if object_type == 'line':
            # Increase the width for visibility when selected
            self.canvas.itemconfig(self.current_object, fill="red", width=3)  
        else:
            # Highlight rectangles with a red outline
            self.canvas.itemconfig(self.current_object, outline="red", width=2)
        
        self.last_object = self.current_object
        self.start_x, self.start_y = event.x, event.y
        self.canvas.bind("<B1-Motion>", self.move_object)
        self.canvas.bind("<ButtonRelease-1>", self.release_object)

    def select_object(self, event):
            """ Modified select_object to handle group selection. """
            selected_object = self.canvas.find_closest(event.x, event.y, halo=10)[0]
            is_grouped = any(selected_object in group for group in self.groups.values())
            if is_grouped:
                for group_id, objects in self.groups.items():
                    if selected_object in objects:
                        self.highlight_group(group_id)
                        if self.selected_tool == "delete":
                            self.perform_group_operation(group_id, "delete")
                        elif self.selected_tool == "copy":
                            self.perform_group_operation(group_id, "copy")
                        break
            else:
                if self.selected_tool == "edit":
                    self.edit_object(event)
                elif self.selected_tool == "delete":
                    self.delete_object(event)
                elif self.selected_tool == "copy":
                    self.copy_object(event)
                else:
                    self.prepare_to_move_object(event)
            

    def create_group(self):
        if self.selected_objects:
            new_group_id = self.group_objects(self.selected_objects)
            print(f"Created new group: {new_group_id}")
            # Optionally, clear the selections after grouping
            self.clear_selections()


    def group_objects(self, object_ids):
        """ Group multiple objects together. """
        group_id = f"group_{self.group_id_counter}"
        self.group_id_counter += 1
        self.groups[group_id] = set(object_ids)
        for obj_id in object_ids:
            self.canvas.itemconfig(obj_id, outline='green')  # Visual indication for grouping
        return group_id

    def ungroup_selected_group(self, group_id):
        """Ungroup the currently selected group."""
    # This needs to know which group is selected; let's assume it's already known
        if not self.selected_objects:
            messagebox.showinfo("Ungroup", "No group selected")
            return
        for obj in self.selected_objects:
            group_id = next((gid for gid, objs in self.groups.items() if obj in objs), None)
            if group_id:
                self.ungroup_objects(group_id)
                break

    def perform_group_operation(self, group_id, operation):
        """ Perform an operation on all objects in a group. """
        if group_id in self.groups:
            for obj_id in self.groups[group_id]:
                if operation == "delete":
                    self.canvas.delete(obj_id)
                    del self.objects[obj_id]
                elif operation == "copy":
                    self.copy_object(obj_id)
                elif operation == "move":
                    pass  # Moving is handled separately
            if operation == "delete":
                del self.groups[group_id]
    def highlight_group(self, group_id):
        """ Highlight all objects in a group. """
        if group_id in self.groups:
            for obj_id in self.groups[group_id]:
                self.canvas.itemconfig(obj_id, outline='red', width=2)  # Highlight effect

    def edit_object(self, event):
        if self.last_object:
            self.reset_highlight(self.last_object)
        self.current_object = self.canvas.find_closest(event.x, event.y, halo=10)[0]
        object_type = self.canvas.type(self.current_object)
        current_color = self.canvas.itemcget(self.current_object, "fill" if object_type == 'line' else "outline")
        new_color, corner_style = edit_properties(self.root, current_color, is_line=(object_type == 'line'))
        if new_color:
            if object_type == 'line':
                self.canvas.itemconfig(self.current_object, fill=new_color)
            else:
                self.canvas.itemconfig(self.current_object, outline=new_color)
                if corner_style == "round":
                    self.canvas.itemconfig(self.current_object, outline=new_color, dash=())
                else:
                    self.canvas.itemconfig(self.current_object, outline=new_color, dash=())
    def move_object(self, event):
        if self.current_object:
            dx = event.x - self.start_x
            dy = event.y - self.start_y
            self.canvas.move(self.current_object, dx, dy)
            self.start_x, self.start_y = event.x, event.y

    def release_object(self, event):
        if self.current_object:
            self.reset_highlight(self.current_object)
            self.current_object = None

    def reset_highlight(self, obj):
        object_type = self.canvas.type(obj)
        if object_type == 'line':
        # Reset line width and color to default
                self.canvas.itemconfig(obj, fill='black', width=1)
        else:
            # Reset rectangle or other shapes' outline to default
            self.canvas.itemconfig(obj, outline='black', width=1)


    def copy_object(self, obj):
        offset = 15
        obj_info = self.objects[obj]
        coords = self.canvas.coords(obj)
        new_coords = [coord + offset for coord in coords]
        if obj_info['type'] == 'line':
            new_obj = self.canvas.create_line(*new_coords, fill='black', tags=str(self.object_id))
        elif obj_info['type'] == 'rectangle':
            new_obj = self.canvas.create_rectangle(*new_coords, outline='black', tags=str(self.object_id))
        self.objects[new_obj] = {'type': obj_info['type'], 'coordinates': new_coords}
        self.object_id += 1

    def open_file(self):
        filename = filedialog.askopenfilename(title="Open File", filetypes=[("Text files", "*.txt")])
        if filename:
            self.canvas.delete("all")  # Clear the current canvas
            self.objects.clear()  # Also clear the objects dictionary to prevent referencing old objects.

            with open(filename, "r") as file:
                for line in file:
                    parts = line.strip().split()
                    if len(parts) < 6:  # Ensure there are enough parts to parse
                        print("Skipped a line due to insufficient data:", line)
                        continue  # Skip this line if not enough parts

                    shape_type = parts[0]
                    x1, y1, x2, y2 = map(int, parts[1:5])
                    color = self.color_code_to_rgb(parts[5])
                    obj = None  # Initialize obj to None for safety

                    if shape_type == "line":
                        obj = self.canvas.create_line(x1, y1, x2, y2, fill=color)
                    elif shape_type == "rectangle":
                        obj = self.canvas.create_rectangle(x1, y1, x2, y2, outline=color)
                    else:
                        print("Unrecognized shape type:", shape_type)
                        continue  # Skip unrecognized shape types

                    if obj is not None:
                        # Store the object with its properties only if it has been created
                        self.objects[obj] = {'type': shape_type, 'coordinates': (x1, y1, x2, y2), 'color': color}
                    else:
                        print("Failed to create object for line:", line)

    def save_file(self):
        filename = filedialog.asksaveasfilename(title="Save File", filetypes=[("Text files", "*.txt")])
        if filename:
            with open(filename, "w") as file:
                for obj, details in self.objects.items():
                    x1, y1, x2, y2 = self.canvas.coords(obj)
                    shape_type = details['type']
                    color = self.rgb_to_color_code(self.canvas.itemcget(obj, "fill"))
                    line = f"{shape_type} {int(x1)} {int(y1)} {int(x2)} {int(y2)} {color}\n"
                    file.write(line)
            self.is_saved = True

    def color_code_to_rgb(self, code):
        return {"k": "black", "r": "red", "g": "green", "b": "blue"}.get(code, "black")

    def rgb_to_color_code(self, rgb):
        return {v: k for k, v in {"k": "black", "r": "red", "g": "green", "b": "blue"}.items()}.get(rgb, "k")

    def run(self):
        if len(sys.argv) > 1:
            self.open_file_via_arg(sys.argv[1])
        self.root.mainloop()
        
    def on_close(self):
        if not self.is_saved:
            response = messagebox.askyesnocancel("Quit", "You have unsaved changes. Save before quitting?")
            if response:  # Yes, save changes
                self.save_file()
                self.root.destroy()
            elif response is None:  # Cancel
                return
        self.root.destroy()
    def open_file_via_arg(self, filename):
        try:
            with open(filename, "r") as file:
                for line in file:
                    parts = line.strip().split()
                    shape_type = parts[0]
                    x1, y1, x2, y2 = map(int, parts[1:5])
                    color = self.color_code_to_rgb(parts[5])
                    if shape_type == "line":
                        obj = self.canvas.create_line(x1, y1, x2, y2, fill=color)
                    elif shape_type == "rect":
                        corner_style = parts[6]
                        obj = self.canvas.create_rectangle(x1, y1, x2, y2, outline=color)
                    self.objects[obj] = {'type': shape_type, 'coordinates': (x1, y1, x2, y2), 'color': color}
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load file: {filename}\n{str(e)}")
    def export_to_xml(self):
        root = ET.Element("Drawing")
        for obj, details in self.objects.items():
            if details['type'] == 'line':
                line = ET.SubElement(root, "line")
                begin = ET.SubElement(line, "begin")
                ET.SubElement(begin, "x").text = str(self.canvas.coords(obj)[0])
                ET.SubElement(begin, "y").text = str(self.canvas.coords(obj)[1])
                end = ET.SubElement(line, "end")
                ET.SubElement(end, "x").text = str(self.canvas.coords(obj)[2])
                ET.SubElement(end, "y").text = str(self.canvas.coords(obj)[3])
                ET.SubElement(line, "color").text = self.rgb_to_color_code(self.canvas.itemcget(obj, "fill"))
            elif details['type'] == 'rectangle':
                rect = ET.SubElement(root, "rectangle")
                upper_left = ET.SubElement(rect, "upper-left")
                ET.SubElement(upper_left, "x").text = str(self.canvas.coords(obj)[0])
                ET.SubElement(upper_left, "y").text = str(self.canvas.coords(obj)[1])
                lower_right = ET.SubElement(rect, "lower-right")
                ET.SubElement(lower_right, "x").text = str(self.canvas.coords(obj)[2])
                ET.SubElement(lower_right, "y").text = str(self.canvas.coords(obj)[3])
                ET.SubElement(rect, "color").text = self.rgb_to_color_code(self.canvas.itemcget(obj, "outline"))
                ET.SubElement(rect, "corner").text = details.get('corner_style', 'square')
        
        tree = ET.ElementTree(root)
        filename = filedialog.asksaveasfilename(title="Export to XML", filetypes=[("XML Files", "*.xml")])
        if filename:
            tree.write(filename)

root = tk.Tk()
app = DrawingApp(root)
app.run()
