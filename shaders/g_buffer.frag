#version 330 core
#extension GL_ARB_bindless_texture : enable

layout (location = 0) out vec3 gPosition;
layout (location = 1) out vec3 gNormal;
layout (location = 2) out vec3 guv;

in vec3 fragPos;
in vec3 normal;
in vec2 uv;

uniform sampler2DArray textureArray;

uniform int i;
// 
// struct texture_sampler {
//     layout (bindless_sampler) sampler2D texture;
// };
// 
// uniform texture_sampler textures[3];

void main() {
    // Store the position to the gbuffer texture
    gPosition = fragPos;
    // Store the normal to the gbuffer texture
    gNormal = normal;
    // Store the uv to the gbuffer texture
    guv = texture(textureArray, vec3(uv, i)).rgb;
    //guv = vec3(uv, 0);
}