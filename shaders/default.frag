#version 330 core

layout (location = 0) out vec4 fragColor;

in vec2 uv_0;
in vec3 normal;
in vec3 fragPos;
in vec4 shadowCoord;


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


#define maxNumPointLights 100
uniform int numLights;
uniform Material material;
uniform DirectionalLight dir_light;
uniform PointLight pointLights[maxNumPointLights];
uniform sampler2DShadow shadowMap;
uniform vec2 u_resolution;
uniform vec3 view_pos;


float standardLightIntensity = 0.5;
float cellLightIntensity = 0.5;
float PLR = 3.0; // Point Light Range


float getSoftShadowX16() {
    float shadow = 0.0;

    vec2 pixelOffset = 1 / u_resolution;
    float swidth = 1.0;
    float endp = swidth * 1.5;
    for (float y = -endp; y <= endp; y += swidth){
        for (float x = -endp; x <= endp; x += swidth){
            shadow += textureProj(shadowMap, shadowCoord + vec4(x * pixelOffset.x * shadowCoord.w, y * pixelOffset.y * shadowCoord.w, 0.0, 0.0));
        }
    }
    return shadow / (16.0);
}


float clamp_value(float value){
     if (value > 0.6){
        value = 1.0;
    }
    else if (value > 0.3){
        value = 0.5;
    }
    else if (value > 0.0){
        value = 0.33;
    }
    else {
        value = 0.0;
    }
    return value;
}


vec3 CalcDirLight(DirectionalLight light, vec3 normal, vec3 viewDir){
    float gamma = 2.2;

    vec3 lightDir = normalize(-light.direction);

    float diff = max(dot(normal, lightDir), 0.0);
    float cellDiff = clamp_value(diff);

    vec3 reflectDir = reflect(-lightDir, normal);
    float spec = pow(max(dot(viewDir, reflectDir), 0.0), material.spec_const);

    vec3 ambient = light.a * light.color * pow(vec3(texture(material.d, uv_0)), vec3(gamma));;
    vec3 diffuse = light.d * cellDiff * light.color * pow(vec3(texture(material.d, uv_0)), vec3(gamma));
    vec3 specular = light.s * spec * light.color * vec3(texture(material.s, uv_0));


    float shadow = getSoftShadowX16();

    return (ambient + (diffuse + specular) * shadow);
}


vec3 CalcPointLight(PointLight light, vec3 normal, vec3 fragPos, vec3 viewDir){

    if (!(light.pos.x - PLR < fragPos.x && fragPos.x < light.pos.x + PLR && light.pos.y - PLR < fragPos.y && fragPos.y < light.pos.y + PLR && light.pos.z - PLR < fragPos.z && fragPos.z < light.pos.z + PLR)) {
        return vec3(0);
    }

    float gamma = 2.2;

    vec3 lightDir = normalize(light.pos - fragPos);

    float diff = max(dot(normal, abs(lightDir)), 0.0);
    float cellDiff = clamp_value(diff);

    vec3 reflectDir = reflect(-lightDir, normal);
    float spec = pow(max(dot(viewDir, reflectDir), 0.0), material.spec_const);

    float distance = length(light.pos - fragPos);
    float attenuation = 1.0 / (light.constant + light.linear * distance + light.quadratic * (distance * distance));

    vec3 ambient = light.a * light.color * pow(vec3(texture(material.d, uv_0)), vec3(gamma));
    vec3 diffuse = light.d * cellDiff * light.color * pow(vec3(texture(material.d, uv_0)), vec3(gamma));
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
    for(int i = 0; i < numLights; i++)
        result += CalcPointLight(pointLights[i], normal, fragPos, viewDir);  

    fragColor = vec4(result, 1.0);
    fragColor.rgb = pow(fragColor.rgb, vec3(1.0/gamma));
}