import numpy as np
import moderngl as mgl
from scripts.editor.editor_ui import EditorUI
from scripts.editor.editor_input import InputHandler
from scripts.editor.font_renderer import FontRenderer
from scripts.editor.viewport_dimensions import ViewportDimensions
from scripts.camera import Camera


class Editor:
    def __init__(self, engine) -> None:
        # Reference to the engine
        self.engine = engine
        self.ctx    = engine.ctx

        # Loads a vao (independent from the engine) for displaying UI
        self.load_vao()

        # UI rendering/input data
        self.viewport_dim = ViewportDimensions(.05, .2, .2, .2)  # Locations of the editor windows

        # Handlers
        self.font = FontRenderer()
        self.input = InputHandler(self)
        self.ui = EditorUI(self)

        # Resize viewport callback
        self.viewport_dim.callback = self.viewport_resize
        
        # Create a camera for the editor viewport and override the scene camera
        self.camera = Camera(self.engine, (0, 0, 0))
        self.engine.project.current_scene.camera = self.camera

        # Will update the scene with the editors attributes
        self.window_resize()

    def render(self):
        """
        Renders the editor UI
        """
        
        self.ui.render()

    def update(self):
        """
        Updates editor inputs
        """
        
        self.input.update()

    def load_vao(self):
        """
        Loads a vbo, program, and vao for rendering UI. VAO is independent from the engine.
        """
        
        # MGL render
        self.frame_vertex_data = np.array([-1.0, 1.0, 0.0, 0.0, 1.0, -1.0, -1.0, 0.0, 0.0, 0.0, 1.0, -1.0, 0.0, 1.0, 0.0, 1.0, 1.0, 0.0, 1.0, 1.0, -1.0, 1.0, 0.0, 0.0, 1.0, 1.0, -1.0, 0.0, 1.0, 0.0], dtype='f4')
        self.vbo = self.ctx.buffer(self.frame_vertex_data)

        # Read the shaders
        with open(f'shaders/editor.vert') as file:
            vertex_shader   = file.read()
        with open(f'shaders/editor.frag') as file:
            fragment_shader = file.read()
        # Load shader program
        self.program = self.ctx.program(vertex_shader=vertex_shader, fragment_shader=fragment_shader)

        # Load vao
        self.vao = self.ctx.vertex_array(self.program, [(self.vbo, '3f 2f', *['in_position', 'in_uv'])], skip_errors=True)

    def window_resize(self):
        """
        Called when the window or viewport is resized. Resets the viewports and camera.
        """
        
        self.use_canera()
        self.ui.window_resize()

        # self.ui.set_viewports()
        # self.ui.set_surface_texture()

    def viewport_resize(self):
        self.use_canera()
        self.ui.set_viewports()
        self.ui.program['engineTexture'] = 1
        self.engine.project.current_scene.vao_handler.frame_texture.use(location=1)

    def use_canera(self):
        """
        Updates the aspect ratio and projection matrix of the camera.
        """
        
        # Updated aspect ratio of the viewport
        self.camera.aspect_ratio = ((self.viewport_dim.width * self.engine.win_size[0]) / (self.viewport_dim.height * self.engine.win_size[1]))
        # Projection matrix
        self.camera.m_proj = self.camera.get_projection_matrix()

        self.engine.project.current_scene.use(camera=False)