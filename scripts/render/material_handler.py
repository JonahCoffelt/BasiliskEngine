import glm

class MaterialHandler:
    def __init__(self, scene) -> None:
        self.scene        = scene
        self.texture_ids  = scene.project.texture_handler.texture_ids
        self.programs     = scene.vao_handler.shader_handler.programs
        self.materials    = {}
        self.material_ids = {}

        self.add("base", ambient=(0.8, 0.8, 0.8), normal_map="normal_map")

    def add(self, name, ambient: tuple=(1, 1, 1), diffuse: tuple=(1, 1, 1), specular: tuple=(1, 1, 1), specular_exponent: float=32, alpha: float=1, albedo_map=None, specular_map=None, normal_map=None):
        mtl = Material(ambient, diffuse, specular, specular_exponent, alpha, albedo_map, specular_map, normal_map)
        self.material_ids[name] = len(self.material_ids)
        self.materials[name] = mtl

    def write(self, program):
        program = self.programs[program]
        for i, mtl in enumerate(list(self.materials.values())):
            mtl.write(program, self.texture_ids, i)
            self.material_ids[mtl] = i


class Material:
    def __init__(self, ambient: tuple, diffuse: tuple, specular: tuple, specular_exponent: float, alpha: float, albedo_map=None, specular_map=None, normal_map=None) -> None:
        # Numberic attributes
        self.ambient:           glm.vec3    = glm.vec3(ambient )
        self.diffuse:           glm.vec3    = glm.vec3(diffuse )
        self.specular:          glm.vec3    = glm.vec3(specular)
        self.specular_exponent: glm.float32 = glm.float32(specular_exponent)
        self.alpha:             glm.float32 = glm.float32(alpha)

        # Texture Maps
        if not albedo_map:
            self.albedo_map     = None
            self.has_albedo_map = glm.int32(0)
        else:
            self.albedo_map: str = albedo_map
            self.has_albedo_map  = glm.int32(1)

        if not specular_map:
            self.specular_map     = None
            self.has_specular_map = glm.int32(0)
        else:
            self.specular_map: str = specular_map
            self.has_specular_map  = glm.int32(1)

        if not normal_map:
            self.normal_map     = None
            self.has_normal_map = glm.int32(0)
        else:
            self.normal_map: str = normal_map
            self.has_normal_map  = glm.int32(1)

    def write(self, program, texture_ids, i=0):
        program[f'materials[{i}].ambient'        ].write(self.ambient)
        program[f'materials[{i}].diffuse'         ].write(self.diffuse)
        program[f'materials[{i}].specular'        ].write(self.specular)
        program[f'materials[{i}].specularExponent'].write(self.specular_exponent)
        program[f'materials[{i}].alpha'           ].write(self.alpha)

        program[f'materials[{i}].hasAlbedoMap'  ].write(self.has_albedo_map)
        #program[f'materials[{i}].hasSpecularMap'].write(self.has_specular_map)
        program[f'materials[{i}].hasNormalMap'  ].write(self.has_normal_map)

        if self.has_albedo_map  : program[f'materials[{i}].albedoMap'  ].write(glm.vec2(texture_ids[self.albedo_map]))
        #if self.has_specular_map: program[f'materials[{i}].specularMap'].write(glm.vec2(texture_ids[self.specular_map]))
        if self.has_normal_map  : program[f'materials[{i}].normalMap'  ].write(glm.vec2(texture_ids[self.normal_map]))
