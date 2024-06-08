#version 330 core

layout (location = 0) out vec4 fragColor;

in vec2 uv;

uniform sampler2D gPosition;
uniform sampler2D gNormal;
uniform sampler2D gAlbedo;

uniform vec3 cameraPosition;


struct DirLight {
    vec3 direction;
  
    vec3 color;

    float ambient;
    float diffuse;
    float specular;
};  

struct PointLight{
    vec3 position;

    vec3 color;

    float constant;
    float linear;
    float quadratic;  

    float ambient;
    float diffuse;
    float specular;
    float radius;
};


vec3 CalcDirLight(DirLight light, vec3 normal, vec3 viewDir, vec3 albedo) {
    vec3 lightDir = normalize(-light.direction);
    // diffuse
    float diff = max(dot(normal, lightDir), 0.0);
    // specular
    vec3 reflectDir = reflect(-lightDir, normal);
    float spec = pow(max(dot(viewDir, reflectDir), 0.0), 16);
    // result
    vec3 ambient  = light.ambient  * albedo * light.color;
    vec3 diffuse  = light.diffuse  * diff * albedo * light.color;
    vec3 specular = light.specular * spec * albedo * light.color;
    return (ambient + diffuse + specular);
}

vec3 CalcPointLight(PointLight light, vec3 normal, vec3 fragPos, vec3 viewDir, vec3 albedo)
{
    vec3 lightDir = normalize(light.position - fragPos);
    // diffuse
    float diff = max(dot(normal, lightDir), 0.0);
    // specular
    vec3 reflectDir = reflect(-lightDir, normal);
    float spec = pow(max(dot(viewDir, reflectDir), 0.0), 24);
    // attenuation
    float distance    = length(light.position - fragPos);
    float attenuation = 1.0 / (light.constant + light.linear * distance + light.quadratic * (distance * distance));    
    // result
    vec3 ambient  = light.ambient  * albedo * light.color;
    vec3 diffuse  = light.diffuse  * diff * albedo * light.color;
    vec3 specular = light.specular * spec * albedo * light.color;
    ambient  *= attenuation;
    diffuse  *= attenuation;
    specular *= attenuation;
    return (ambient + diffuse + specular);
} 


uniform DirLight dirLight;
#define maxLights 100
uniform int numPointLights;
uniform PointLight pointLights[maxLights];


void main() {
    vec3 position = texture(gPosition, uv).rgb;
    vec3 normal = texture(gNormal, uv).rgb;
    vec3 albedo = texture(gAlbedo, uv).rgb;

    vec3 viewDir = vec3(normalize(cameraPosition - position));

    vec3 light_result = CalcDirLight(dirLight, normal, viewDir, albedo);
    for(int i = 0; i < numPointLights; i++){
        float distance = length(pointLights[i].position - position);
        if (distance < pointLights[i].radius){
            light_result += CalcPointLight(pointLights[i], normal, position, viewDir, albedo);
        }
    }
        


    fragColor = vec4(light_result, 1.0);
}