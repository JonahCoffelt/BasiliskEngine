import pygame as pg


class Inspector:
    def __init__(self, editor, ui) -> None:
        # Reference to enviornment
        self.editor       = editor
        self.engine       = self.editor.engine
        self.input        = editor.input
        self.ui           = ui
        self.viewport_dim = editor.viewport_dim

        # Selection attributes
        self.scroll_value = 0

        # Display attributes
        self.top_buffer = 50
        self.list_item_height = 30
        self.padding = 3
        self.indent_pixels = 10

        self.set_surf()  # Set the surface for drawing

    def render(self):
        """Clears the viewport and renders all elements"""
        # Clear the window
        self.surf.fill(self.ui.primary)

        objects = self.engine.project.current_scene.object_handler.objects
        object_index = self.ui.hierarchy.selected_object_index
        if 0 <= object_index < len(objects): obj = objects[object_index]
        else: obj = None

        # Draw the top bar of the hierarchy view
        pg.draw.rect(self.surf, self.ui.accent, (0, 0, self.dim[0], self.top_buffer - self.padding * 2))

        # List of all currently rendered attribute boxes
        self.attribute_boxes = []

        # Transform
        if obj:
            start_x, start_y = 45, self.top_buffer
            w, h = (self.dim[0] - start_x - 15) // 3, self.list_item_height
            padding = 3
            # Position
            self.editor.font.render_text(self.surf, (padding, start_y + h * 0 + h/2), 'Pos', size=0)
            self.attribute_boxes.append((obj.position.x, (start_x + w * 0 + padding, start_y + h * 0 + padding, w - padding * 2, h - padding * 2), 'position_x'))
            self.attribute_boxes.append((obj.position.y, (start_x + w * 1 + padding, start_y + h * 0 + padding, w - padding * 2, h - padding * 2), 'position_y'))
            self.attribute_boxes.append((obj.position.z, (start_x + w * 2 + padding, start_y + h * 0 + padding, w - padding * 2, h - padding * 2), 'position_z'))
            # Rotation
            self.editor.font.render_text(self.surf, (padding, start_y + h * 1 + h/2), 'Rot', size=0)
            self.attribute_boxes.append((obj.rotation.x, (start_x + w * 0 + padding, start_y + h * 1 + padding, w - padding * 2, h - padding * 2), 'rotation_x'))
            self.attribute_boxes.append((obj.rotation.y, (start_x + w * 1 + padding, start_y + h * 1 + padding, w - padding * 2, h - padding * 2), 'rotation_y'))
            self.attribute_boxes.append((obj.rotation.z, (start_x + w * 2 + padding, start_y + h * 1 + padding, w - padding * 2, h - padding * 2), 'rotation_z'))
            # Scale
            self.editor.font.render_text(self.surf, (padding, start_y + h * 2 + h/2), 'Scale', size=0)
            self.attribute_boxes.append((obj.scale.x   , (start_x + w * 0 + padding, start_y + h * 2 + padding, w - padding * 2, h - padding * 2), 'scale_x'   ))
            self.attribute_boxes.append((obj.scale.y   , (start_x + w * 1 + padding, start_y + h * 2 + padding, w - padding * 2, h - padding * 2), 'scale_y'   ))
            self.attribute_boxes.append((obj.scale.z   , (start_x + w * 2 + padding, start_y + h * 2 + padding, w - padding * 2, h - padding * 2), 'scale_z'   ))

        for box in self.attribute_boxes:
            self.render_attribute_box(*box)

        # Drae the outline of the window
        pg.draw.rect(self.surf, self.ui.outline, (0, 0, self.dim[0], self.dim[1]), 1)
        if 0 <= object_index < len(objects): self.editor.font.render_text(self.surf, (self.dim[0] // 2, self.top_buffer // 2), objects[object_index].name, color=self.editor.ui.text_color, size=1, center_width=True)

    def render_attribute_box(self, value, rect, attrib_name):
        # Check if the attribute in the box is being edited by the user
        if self.input.selected_text_attrib == attrib_name: 
            color = self.ui.accent
            text = self.input.input_string
        else: 
            color = self.ui.secondary
            text = f'{value:.2f}'
        pg.draw.rect(self.surf, color, rect)
        self.editor.font.render_text(self.surf, (rect[0] + rect[2] / 2, rect[1] + rect[3] / 2), text, size=3, center_width=True)

    def apply_input_string(self):
        objects = self.engine.project.current_scene.object_handler.objects
        object_index = self.ui.hierarchy.selected_object_index
        if 0 <= object_index < len(objects): obj = objects[object_index]
        else: self.input.selected_text_attrib = None; return

        match self.input.selected_text_attrib:
            case 'position_x':
                try:
                    obj.x = float(self.input.input_string)
                except ValueError: ...
            case 'position_y':
                try:
                    obj.y = float(self.input.input_string)
                except ValueError: ...
            case 'position_z':
                try:
                    obj.z = float(self.input.input_string)
                except ValueError: ...
            case 'rotation_x':
                try:
                    obj.rotation.x = float(self.input.input_string)
                except ValueError: ...
            case 'rotation_y':
                try:
                    obj.rotation.y = float(self.input.input_string)
                except ValueError: ...
            case 'rotation_z':
                try:
                    obj.rotation.z = float(self.input.input_string)
                except ValueError: ...
            case 'scale_x':
                try:
                    obj.scale.x = float(self.input.input_string)
                except ValueError: ...
            case 'scale_y':
                try:
                    obj.scale.y = float(self.input.input_string)
                except ValueError: ...
            case 'scale_z':
                try:
                    obj.scale.z = float(self.input.input_string)
                except ValueError: ...
            case _:
                ...
        
        self.input.selected_text_attrib = None

    def get_input(self) -> None:
        if self.engine.prev_mouse_buttons[0] and not self.engine.mouse_buttons[0]:
            # Get the mouse position in the window
            self.apply_input_string()
            self.input.selected_text_attrib = None
            self.input.input_string = ''
            self.ui.do_update_texture = True
            mouse_x, mouse_y = self.engine.mouse_position[0] - (1 - self.editor.viewport_dim.right) * self.engine.win_size[0], self.engine.mouse_position[1] - self.editor.viewport_dim.top * self.engine.win_size[1]
            for box in self.attribute_boxes:
                rect = box[1]
                if rect[0] <= mouse_x < rect[0] + rect[2] and rect[1] <= mouse_y < rect[1] + rect[3]:
                    self.input.selected_text_attrib = box[2]
                    self.input.input_string = ''
                    self.ui.do_update_texture = True
                    break
      

    def scroll(self, value) -> None:
        ...

    def set_surf(self) -> None:
        """Sets the viewport surface for drawing onto."""
        self.dim = self.viewport_dim.get_inspector_pixels(self.engine.win_size)
        self.surf = pg.Surface(self.dim).convert_alpha()