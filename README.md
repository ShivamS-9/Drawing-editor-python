# Drawing Editor 

## Overview

The Drawing Editor is a versatile 2D drawing application prototype designed to support various drawing and editing functionalities. It allows users to create, manipulate, and manage graphical objects like lines and rectangles on a canvas, with support for grouping, editing, and saving their creations.

While this prototype supports only **lines** and **rectangles**, the design is extensible, enabling easy integration of additional drawing primitives (e.g., ellipses, curves) and operations (e.g., rotation, scaling) in the future.

---

## Features

### Drawing Tools
- **Line Tool**: Draw straight lines on the canvas.
- **Rectangle Tool**: Draw rectangles on the canvas.

### Editing Tools
- **Select Tool**: Select individual objects or groups of objects for further operations.
- **Edit Tool**: Modify the properties of selected objects (e.g., color and corner style).

### Object Operations
- **Delete**: Remove objects or groups from the canvas.
- **Copy**: Duplicate selected objects or groups.

### Grouping
- **Create Group**: Combine multiple selected objects into a group.
- **Ungroup**: Separate objects in a group.

### Object Movement
- **Move Objects**: Drag and reposition objects or groups on the canvas.

### Object Properties
- **Edit Properties**: Change the color and, for rectangles, the corner style (square or rounded).

### File Operations
- **Save**: Save the current canvas state.
- **Open**: Load a previously saved canvas.
- **Export to XML**: Export canvas data to an XML file for external use.

### Visual Feedback
- Highlight selected objects or groups using outlines and colors to distinguish them from others.
### Export to XML
- Drawings can be exported to an XML file for use in other applications.

## Usage
1. **Run the Application**: Start the application by executing the Python script.
2. **Select Tools**: Choose tools like `line`, `rectangle`, `select`, or `edit` from the menu.
3. **Perform Operations**: Use the canvas to draw, edit, group, or manage objects.
4. **File Management**: Save, open, or export your work using the file menu.

## Dependencies
- Python 3.x
- Tkinter library (bundled with Python)

## How to Run
1. Ensure Python is installed on your system.
2. Save the script to a file named `drawing_editor.py`.
3. Run the script using the command:
   ```bash
   python drawing_editor.py
