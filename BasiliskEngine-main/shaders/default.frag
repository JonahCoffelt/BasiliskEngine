#version 330 core

layout (location = 0) out vec4 fragColor;

in vec2 uv;
in vec3 normal;
in vec3 fragPos;

void main() {
    fragColor = vec4(uv, 1.0, 1.0);
}