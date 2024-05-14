class DefferedRenderer:
    def __init__(self, engine, project) -> None:
        self.engine = engine
        self.project = project
        self.ctx = engine.ctx

        self.vao = self.project.vao_handler.vaos['frame']

        size = self.engine.win_size

        self.depth_texture = self.ctx.depth_texture(size)
        self.position_texture = self.ctx.texture(size, 4)
        self.normal_texture = self.ctx.texture(size, 3)
        self.uv_texture = self.ctx.texture(size, 3)

        self.framebuffer = self.ctx.framebuffer([self.position_texture, self.normal_texture, self.uv_texture], self.depth_texture)

    def use(self):
        self.framebuffer.clear(color=(0.08, 0.16, 0.18))
        self.framebuffer.use()

    def render(self):
        # Set screen to render target
        self.ctx.screen.use()

        # Send gbuffer textures as uniforms
        self.vao.program['gPosition'] = 0
        self.position_texture.use(location=0)
        self.vao.program['gNormal'] = 1
        self.normal_texture.use(location=1)
        self.vao.program['guv'] = 2
        self.uv_texture.use(location=2)

        # Renders the frame
        self.vao.render()