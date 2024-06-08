import glm
import random
import math


class LightHandler:
    def __init__(self):
        self.dir_light = DirectionalLight(ambient=.2, diffuse=.4, specular=1.0)
        self.point_lights = [PointLight(pos=(random.randrange(-5, 85), random.randrange(-5, 85), random.randrange(-5, 85)), color=(random.uniform(0.0, 1.0), random.uniform(0.0, 1.0), random.uniform(0.0, 1.0))) for i in range(0)]

    def write(self, program, dir=True, point=True):
        if dir:
            program['dirLight.direction'].write(self.dir_light.dir)
            program['dirLight.color'].write(self.dir_light.color)
            program['dirLight.ambient'].write(self.dir_light.ambient)
            program['dirLight.diffuse'].write(self.dir_light.diffuse)
            program['dirLight.specular'].write(self.dir_light.specular)
        if point:
            program[f'numPointLights'].write(glm.int32(len(self.point_lights)))
            for i, light in enumerate(self.point_lights):
                program[f'pointLights[{i}].position'].write(light.pos)
                program[f'pointLights[{i}].constant'].write(light.constant)
                program[f'pointLights[{i}].linear'].write(light.linear)
                program[f'pointLights[{i}].quadratic'].write(light.quadratic)
                program[f'pointLights[{i}].color'].write(light.color)
                program[f'pointLights[{i}].ambient'].write(light.ambient)
                program[f'pointLights[{i}].diffuse'].write(light.diffuse)
                program[f'pointLights[{i}].specular'].write(light.specular)
                program[f'pointLights[{i}].radius'].write(light.radius)

class Light:
    def __init__(self, ambient=0.2, diffuse=0.5, specular=1.0, color=(1.0, 1.0, 1.0)):
        self.color = glm.vec3(color)
        self.ambient = glm.float32(ambient)
        self.diffuse = glm.float32(diffuse)
        self.specular = glm.float32(specular)

class DirectionalLight(Light):
    def __init__(self, direction=(1.5, -2.0, 1.0), ambient=0.4, diffuse=0.6, specular=1.0, color=(1.0, 1.0, 1.0)):
        super().__init__(ambient, diffuse, specular, color)
        self.dir = glm.vec3(direction)
        self.position = glm.vec3(150, 100, -150)
        # View matrix
        self.m_view_light = self.get_view_matrix()
    
    def get_view_matrix(self):
        return glm.lookAt(self.position, self.dir, glm.vec3(0, 1, 0) )

class PointLight(Light):
    def __init__(self, pos=(0.0, 0.0, 0.0), constant=1.0, linear=0.09, quadratic=0.032, ambient=0.0, diffuse=1.5, specular=1.0, color=(1.0, 1.0, 1.0)):
        super().__init__(ambient, diffuse, specular, color)
        self.pos = glm.vec3(pos)
        self.constant = glm.float32(constant)
        self.linear = glm.float32(linear)
        self.quadratic = glm.float32(quadratic)

        self.light_max = max(color)
        self.radius = glm.float32((-linear + math.sqrt(linear ** 2 - 4 * quadratic * (constant - (256.0/5.0) * self.light_max))) / (4 * quadratic))
