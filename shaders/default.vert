#version 330 core

layout (location = 0) in vec3 in_position;
layout (location = 1) in vec3 in_normal;
layout (location = 2) in vec2 in_texcoord;

layout (location = 4) in vec3 in_instance_position;
layout (location = 5) in vec3 in_instance_scale;
layout (location = 6) in vec3 in_instance_rotation;

out vec2 uv;
out vec3 normal;
out vec3 fragPos;

uniform mat4 m_proj;
uniform mat4 m_view;

void main() {
    vec3 position = in_position + in_instance_position;
    vec3 rot = in_instance_rotation;

    mat4 m_rot = mat4(
        cos(rot.z) * cos(rot.y), cos(rot.z) * sin(rot.y) * sin(rot.x) - sin(rot.z) * cos(rot.x), cos(rot.z) * sin(rot.y) * cos(rot.x) + sin(rot.z) * sin(rot.x), 0,
        sin(rot.z) * cos(rot.y), sin(rot.z) * sin(rot.y) * sin(rot.x) + cos(rot.z) * cos(rot.x), sin(rot.z) * sin(rot.y) * cos(rot.x) - cos(rot.z) * sin(rot.x), 0,
        -sin(rot.y)            , cos(rot.y) * sin(rot.x)                                       , cos(rot.y) * cos(rot.x)                                       , 0,
        0                      , 0                                                             , 0                                                             , 1
    );

    mat4 m_trans = mat4(
        1, 0, 0, 0,
        0, 1, 0, 0,
        0, 0, 1, 0,
        in_instance_position.x, in_instance_position.y, in_instance_position.z, 1
    );

    mat4 m_scale = mat4(
        in_instance_scale.x, 0, 0, 0,
        0                  , in_instance_scale.y, 0, 0,
        0                  , 0                  , in_instance_scale.z, 0,
        0                  , 0                  , 0                  , 1
    );

    mat4 m_model = m_trans * m_rot * m_scale;

    uv = in_texcoord;
    fragPos = vec3(m_model * vec4(in_position, 1.0));
    normal = normalize(mat3(transpose(inverse(m_model))) * in_normal);  
    gl_Position = m_proj * m_view * m_model * vec4(in_position, 1.0);
}