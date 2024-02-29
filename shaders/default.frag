#version 330 core

layout (location = 0) out vec4 fragColor;

in vec2 uv_0;
in vec3 normal;
in vec3 fragPos;
in vec4 shadowCoord;


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
uniform sampler2DShadow shadowMap;
uniform vec2 u_resolution;


float lookup(float ox, float oy){
    vec2 pixelOffset = 1 / u_resolution;
    return textureProj(shadowMap, shadowCoord + vec4(ox * pixelOffset.x * shadowCoord.w,
                                                     oy * pixelOffset.y * shadowCoord.w, 0.0, 0.0));
}

float getShadow(){
    float shadow = textureProj(shadowMap, shadowCoord);
    return shadow;
}

float getSoftShadowX16() {
    float shadow;
    float swidth = 1.0;
    float endp = swidth * 1.5;
    for (float y = -endp; y <= endp; y += swidth){
        for (float x = -endp; x <= endp; x += swidth){
            shadow += lookup(x, y);
        }
    }
    return shadow / 16.0;
}


vec3 CalcDirLight(DirectionalLight light, vec3 normal, vec3 viewDir){
    float gamma = 2.2;

    vec3 lightDir = normalize(-light.direction);

    float diff = max(dot(normal, lightDir), 0.0);

    vec3 reflectDir = reflect(-lightDir, normal);
    float spec = pow(max(dot(viewDir, reflectDir), 0.0), material.spec_const);

    vec3 ambient = light.a * light.color * pow(vec3(texture(material.d, uv_0)), vec3(gamma));;
    vec3 diffuse = light.d * diff * light.color * pow(vec3(texture(material.d, uv_0)), vec3(gamma));
    vec3 specular = light.s * spec* light.color * vec3(texture(material.s, uv_0));

    float shadow = getSoftShadowX16();
    shadow = getShadow();

    return (ambient + (diffuse + specular) * shadow);
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