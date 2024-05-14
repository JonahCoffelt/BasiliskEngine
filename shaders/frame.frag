#version 330 core
#extension GL_ARB_bindless_texture : enable

layout (location = 0) out vec4 fragColor;

in vec2 uv;

uniform sampler2D gPosition;
uniform sampler2D gNormal;
uniform sampler2D guv;


//struct texture_sampler {
//    layout (bindless_sampler) sampler2D texture;
//};
//
//uniform texture_sampler textures[3];


void main() {
    vec4 position = texture(gPosition, uv);
    vec3 normal = texture(gNormal, uv).rgb;
    vec3 albedo = texture(guv, uv).rgb;

    //vec3 albedo = texture(textures[int(uvCoord.b)].texture, uvCoord.rg).rgb;

    vec3 lightDir = normalize(vec3(10.0, 10.0, 10.0) - position.xyz);
    vec3 reflectDir = reflect(-lightDir, normal);

    vec3 ambient = vec3(0.3);
    vec3 diffuse = vec3(dot(normal, normalize(vec3(1.5, 1.0, 0.5))));
    vec3 spec = vec3(pow(max(dot(vec3(0.0, 0.0, 0.0), reflectDir), 0.0), 16.0));

    vec3 light = (ambient + diffuse + spec) * albedo;

    fragColor = vec4(light, 1.0);
}