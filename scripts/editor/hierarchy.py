import pygame as pg


class Hierarchy:
    def __init__(self, editor) -> None:
        # Reference to enviornment
        self.editor       = editor
        self.engine       = self.editor.engine
        self.viewport_dim = editor.viewport_dim

        # Selection attributes
        self.scroll_value = 0
        self.selected_object_index = 0

        # Display attributes
        self.top_buffer = 50
        self.indent_pixels = 10
        self.list_item_height = 30
        self.scroll_bar_width = 15
        self.scroll_bar_height = 20
        self.slider_height = 10

        self.set_surf()  # Set the surface for drawing

    def render(self):
        """Clears the viewport and renders all elements"""
        # Clear the window
        self.surf.fill(self.editor.ui.primary)

        # Draw the names of the objects in the scene
        objects = self.engine.project.current_scene.object_handler.objects
        for i in range(min(self.dim[1] // self.list_item_height + 1, len(objects) - max(self.scroll_value // self.list_item_height, 0))):
            self.render_list_item(objects[i + max(self.scroll_value // self.list_item_height, 0)].name, i, highlight=(self.selected_object_index==(i + max(self.scroll_value // self.list_item_height, 0))))

        # Draw Scroll Bar
        padding = 3
        self.scroll_bar_width = 15
        self.scroll_bar_height = self.dim[1] - self.top_buffer - 20
        if len(objects): self.slider_height = self.scroll_bar_height // len(objects)
        else: self.slider_height = self.scroll_bar_height
        pg.draw.rect(self.surf, self.editor.ui.secondary, (padding, self.top_buffer, self.scroll_bar_width - padding * 2, self.dim[1] - self.top_buffer - 10))
        pg.draw.rect(self.surf, self.editor.ui.accent,    (padding, self.top_buffer + (max(self.scroll_value // self.list_item_height, 0) * self.slider_height), self.scroll_bar_width - padding * 2, self.slider_height))

        # Draw the top bar of the hierarchy view
        pg.draw.rect(self.surf, self.editor.ui.accent, (0, 0, self.dim[0], self.top_buffer - padding * 2))
        self.editor.font.render_text(self.surf, (self.dim[0] // 2, self.top_buffer // 2), "Scene", color=self.editor.ui.text_color, size=1, center_width=True)

        # Drae the outline of the window
        pg.draw.rect(self.surf, self.editor.ui.outline, (0, 0, self.dim[0], self.dim[1]), 1)

    def render_list_item(self, text, y_level, indent=0, highlight=False):
        if highlight: pg.draw.rect(self.surf, self.editor.ui.secondary, (15, self.top_buffer + y_level * self.list_item_height - self.scroll_value%self.list_item_height, self.dim[0] - 18, self.list_item_height))
        self.editor.font.render_text(self.surf, (25 + indent * self.indent_pixels, self.top_buffer + y_level * self.list_item_height + self.list_item_height/2 - self.scroll_value%self.list_item_height), text, color=self.editor.ui.text_color, size=0)

    def get_input(self) -> None:
        if self.engine.prev_mouse_buttons[0] and not self.engine.mouse_buttons[0]:
            # Get the mouse position in the window
            mouse_x, mouse_y = self.engine.mouse_position[0], self.engine.mouse_position[1] - self.editor.viewport_dim.top * self.engine.win_size[1]
            # Get the list item index the mouse is in
            self.selected_object_index = int(max(self.scroll_value // self.list_item_height + (mouse_y - self.top_buffer) // self.list_item_height, -1))
            # Update the UI texture
            self.editor.ui.do_update_texture = True

    def scroll(self, value) -> None:
        self.scroll_value = min(max(self.scroll_value - value * 15, 0), self.list_item_height * (len(self.engine.project.current_scene.object_handler.objects) - 1))
        self.editor.ui.do_update_texture = True

    def set_surf(self) -> None:
        """Sets the viewport surface for drawing onto."""
        self.dim = self.viewport_dim.get_hierarchy_pixels(self.engine.win_size)
        self.surf = pg.Surface(self.dim).convert_alpha()