#version 330 core

layout (location = 0) out vec4 fragColor;

in vec2 uv_0;
in vec3 normal;
in vec3 fragPos;


uniform vec3 view_pos;


struct Material {
    sampler2D d;
    sampler2D s;
    float spec_const;
};


struct DirectionalLight {
    vec3 direction;

    vec3 color;
    float a;
    float d;
    float s;
};


struct PointLight {
    vec3 pos;

    float constant;
    float linear;
    float quadratic;

    vec3 color;
    float a;
    float d;
    float s;
};

#define numPointLights 3

uniform Material material;
uniform DirectionalLight dir_light;
uniform PointLight pointLights[numPointLights];

vec3 CalcDirLight(DirectionalLight light, vec3 normal, vec3 viewDir){
    float gamma = 2.2;

    vec3 lightDir = normalize(-light.direction);

    float diff = max(dot(normal, lightDir), 0.0);

    vec3 reflectDir = reflect(-lightDir, normal);
    float spec = pow(max(dot(viewDir, reflectDir), 0.0), material.spec_const);

    vec3 ambient = light.a * light.color * pow(vec3(texture(material.d, uv_0)), vec3(gamma));;
    vec3 diffuse = light.d * diff * light.color * pow(vec3(texture(material.d, uv_0)), vec3(gamma));
    vec3 specular = light.s * spec* light.color * vec3(texture(material.s, uv_0));

    return (ambient + diffuse + specular);
}


vec3 CalcPointLight(PointLight light, vec3 normal, vec3 fragPos, vec3 viewDir){
    float gamma = 2.2;

    vec3 lightDir = normalize(light.pos - fragPos);

    float diff = max(dot(normal, lightDir), 0.0);

    vec3 reflectDir = reflect(-lightDir, normal);
    float spec = pow(max(dot(viewDir, reflectDir), 0.0), material.spec_const);

    float distance = length(light.pos - fragPos);
    float attenuation = 1.0 / (light.constant + light.linear * distance + light.quadratic * (distance * distance));

    vec3 ambient = light.a * light.color * pow(vec3(texture(material.d, uv_0)), vec3(gamma));
    vec3 diffuse = light.d * diff * light.color * pow(vec3(texture(material.d, uv_0)), vec3(gamma));
    vec3 specular = light.s * spec * light.color * vec3(texture(material.s, uv_0));

    ambient *= attenuation;
    diffuse *= attenuation;
    specular *= attenuation;

    diffuse = pow(diffuse, vec3(gamma));

    return (ambient + diffuse + specular);
}



void main() {
    float gamma = 2.2;

    vec3 viewDir = vec3(normalize(view_pos - fragPos));

    vec3 result = CalcDirLight(dir_light, normal, viewDir);
    for(int i = 0; i < numPointLights; i++)
        result += CalcPointLight(pointLights[i], normal, fragPos, viewDir);  

    fragColor = vec4(result, 1.0);
    fragColor.rgb = pow(fragColor.rgb, vec3(1.0/gamma));
}










