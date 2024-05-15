#version 330 core

layout (location = 0) out vec3 gPosition;
layout (location = 1) out vec3 gNormal;
layout (location = 2) out vec3 gAlbedo;

in vec3 fragPos;
in vec3 normal;
in vec2 uv;

uniform vec2 textureID;

struct textArray {
    sampler2DArray array;
};

uniform textArray textureArrays[5];


void main() {
    // Store the position to the gbuffer texture
    gPosition = fragPos;
    // Store the normal to the gbuffer texture
    gNormal = normal;
    // Store the uv to the gbuffer texture
    gAlbedo = texture(textureArrays[int(textureID.x)].array, vec3(uv, textureID.y)).rgb;
}