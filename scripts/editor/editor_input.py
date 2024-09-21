import pygame as pg


class InputHandler:
    def __init__(self, editor) -> None:
        # Reference to the editor
        self.editor = editor
        self.dim =    editor.viewport_dim
        
        # Input attributes
        self.mouse_viewport = None
        """The instance of the viewport that the mouse is currently in."""
        self.mouse_viewport_name: str = None
        """Name of the current mouse viewport. Used for comparisons"""
        self.mouse_lock_position: tuple = (0, 0)
        """Position of the mouse before it is locked (used to restore position when unlocked)"""
        self.camera_active: bool = False
        """Bool determining if the editor camera is being used by the user"""
        self.dragging: str = ''
        """The viewport border name that is currently being dragged. Empty string if none"""
        self.selected_text_attrib = None
        """The attribute that is being edited by text input"""
        self.input_string: str = ''
        """Current value of the text input string"""
        self.input_viewport: str = 'inspector'

    def update(self):
        # Get all input lists from the engine
        keys = self.editor.engine.keys
        prev_keys = self.editor.engine.prev_keys
        mouse_position = self.editor.engine.mouse_position
        mouse_x, mouse_y = mouse_position
        mouse_buttons = self.editor.engine.mouse_buttons
        prev_mouse_buttons = self.editor.engine.prev_mouse_buttons
        win_size = self.editor.engine.win_size

        self.viewports = {
            'toolbar' : self.editor.ui.toolbar,
            'files' : self.editor.ui.project_files_view,
            'hierarchy' : self.editor.ui.hierarchy,
            'inspector' : self.editor.ui.inspector,
            'viewport' : self.editor.ui.viewport
        }

        # Get the current mouse viewport
        if mouse_y < self.dim.top * win_size[1]:
            self.mouse_viewport = self.editor.ui.toolbar
            self.mouse_viewport_name = 'toolbar'
        elif mouse_y > (1 - self.dim.bottom) * win_size[1]:
            self.mouse_viewport = self.editor.ui.project_files_view
            self.mouse_viewport_name = 'files'
        elif mouse_x < self.dim.left * win_size[0]:
            self.mouse_viewport = self.editor.ui.hierarchy
            self.mouse_viewport_name = 'hierarchy'
        elif mouse_x > (1 - self.dim.right) * win_size[0]:
            self.mouse_viewport = self.editor.ui.inspector
            self.mouse_viewport_name = 'inspector'
        else:
            self.mouse_viewport = self.editor.ui.viewport
            self.mouse_viewport_name = 'viewport'

        for event in self.editor.engine.events:
            if event.type == pg.MOUSEWHEEL:
                self.mouse_viewport.scroll(event.y)
            if event.type == pg.KEYDOWN and self.selected_text_attrib:
                if event.key == pg.K_BACKSPACE: self.input_string = self.input_string[:-1]
                elif event.key == pg.K_RETURN: self.viewports[self.input_viewport].apply_input_string()
                elif event.key == pg.K_ESCAPE: 
                    self.input_string = ''
                    self.selected_text_attrib = None
                else: self.input_string += event.unicode
                self.editor.ui.do_update_texture = True

        # Check for viewport dragging
        if mouse_buttons[0]:
            if not self.dragging:
                threshold = 5  # Number of pixels in each direction of a border that a drag can start
                if (1 - self.dim.bottom) * win_size[1] - threshold < mouse_y <= (1 - self.dim.bottom) * win_size[1] + threshold:
                    self.dragging = 'bottom'
                elif self.dim.left * win_size[0] - threshold < mouse_x <= self.dim.left * win_size[0] + threshold and self.dim.top * win_size[1] < mouse_y <= (1 - self.dim.bottom) * win_size[1]:
                    self.dragging = 'left'
                elif (1 - self.dim.right) * win_size[0] - threshold < mouse_x <= (1 - self.dim.right) * win_size[0] + threshold and self.dim.top * win_size[1] < mouse_y <= (1 - self.dim.bottom) * win_size[1]:
                    self.dragging = 'right'
        elif prev_mouse_buttons[0]:
            self.dragging = ''
            self.input_string = ''
            self.selected_text_attrib = None

        match self.dragging:
            case 'bottom':
                self.dim.bottom = min(max(1 - mouse_y / win_size[1], 0.001), 0.9)
            case 'left':
                self.dim.left   = min(max(mouse_x / win_size[0], 0), .95 - self.dim.right)
            case 'right':
                self.dim.right  = min(max(1 - mouse_x / win_size[0], 0), .95 - self.dim.left)

        # Right click
        if mouse_buttons[2] and prev_mouse_buttons[2]: 
            ...
        elif mouse_buttons[2] and self.mouse_viewport_name == 'viewport':
            self.camera_active = True
            pg.mouse.get_rel()
            # Lock mouse
            self.mouse_lock_position = mouse_position
            pg.event.set_grab(True)
            pg.mouse.set_visible(False)
        elif prev_mouse_buttons[2]:
            # Unlock mouse
            pg.event.set_grab(False)
            pg.mouse.set_visible(True)
            if self.camera_active: pg.mouse.set_pos(self.mouse_lock_position)

            self.camera_active = False
        
        
        if not self.camera_active and not self.dragging: self.mouse_viewport.get_input()

        if self.camera_active: self.editor.camera.update()