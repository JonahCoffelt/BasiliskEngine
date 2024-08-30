import glm


class ObjectHandler:
    def __init__(self, project) -> None:
        self.project = project
        self.objects = []

    def render(self):
        for object in self.objects:
            object.render()

    def add(self, vao, texture_key: str, position: tuple, rotation: tuple, scale: tuple):
        texture = glm.vec2(self.project.texture_handler.texture_loactions[texture_key])
        self.objects.append(Object(vao, texture, position, rotation, scale))


class Object:
    def __init__(self, vao, texture, position: tuple, rotation: tuple, scale: tuple) -> None:
        self.vao = vao

        self.texture = texture
        
        self.position = glm.vec3(position)
        self.rotation = glm.vec3(rotation)
        self.scale    = glm.vec3(scale)

        m_model = glm.mat4()
        # Translate
        m_model = glm.translate(m_model, self.position)
        # Rotate
        m_model = glm.rotate(m_model, self.rotation.x, glm.vec3(1, 0, 0))
        m_model = glm.rotate(m_model, self.rotation.y, glm.vec3(0, 1, 0))
        m_model = glm.rotate(m_model, self.rotation.z, glm.vec3(0, 0, 1))
        # Scale
        self.m_model = glm.scale(m_model, self.scale)

    def render(self):
        self.vao.program['m_model'].write(self.m_model)
        self.vao.program['textureID'].write(self.texture)

        self.vao.render()