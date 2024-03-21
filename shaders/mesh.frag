#version 330 core

layout (location = 0) out vec4 fragColor;


in vec3 normal;
in vec3 groundColor;
in vec3 fragPos;
in vec4 shadowCoord;


uniform vec3 view_pos;

const float offset = 1.0 / 300.0;

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

#define numPointLights 4

uniform DirectionalLight dir_light;
uniform PointLight pointLights[numPointLights];
uniform sampler2DShadow shadowMap;
uniform vec2 u_resolution;


float getShadow(){
    float shadow = textureProj(shadowMap, shadowCoord);
    return shadow;
}

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
    else if (value > 0.2){
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
    float diff_cel = clamp_value(diff);

    vec3 reflectDir = reflect(-lightDir, normal);
    float spec = pow(max(dot(viewDir, reflectDir), 0.0), 16);

    vec3 ambient = light.a * light.color * groundColor;
    vec3 diffuse = (light.d * diff_cel * light.color * groundColor) * .5 + (light.d * diff * light.color * groundColor) * .5;
    vec3 specular = light.s * spec * light.color * groundColor * .5;

    float shadow = getSoftShadowX16();

    return (ambient + (diffuse + specular) * (shadow/2 + .5)) + u_resolution.x/100000000;
}


vec3 CalcPointLight(PointLight light, vec3 normal, vec3 fragPos, vec3 viewDir){
    float gamma = 2.2;

    vec3 lightDir = normalize(light.pos - fragPos);

    float diff = max(dot(normal, lightDir), 0.0);

    if (diff > 0.5){
        diff = 1.0;
    }
    else if (diff > 0.2){
        diff = 0.5;
    }
    else if (diff > 0.0){
        diff = 0.33;
    }
    else {
        diff = 0.0;
    }

    vec3 reflectDir = reflect(-lightDir, normal);
    float spec = pow(max(dot(viewDir, reflectDir), 0.0), 16);

    float distance = length(light.pos - fragPos);
    float attenuation = 1.0 / (light.constant + light.linear * distance + light.quadratic * (distance * distance));

    vec3 ambient = light.a * light.color * groundColor;
    vec3 diffuse = light.d * diff * light.color * groundColor + light.d * diff * light.color * .25;
    vec3 specular = light.s * spec * light.color * groundColor;

    ambient *= attenuation;
    diffuse *= attenuation;
    specular *= attenuation;

    diffuse = pow(diffuse, vec3(gamma));

    return (ambient + diffuse);
}



void main() {

    //float height = fragPos.y;
    //if (height > 0.1) {
    //    height += ((sin(fragPos.x * 7) + cos(fragPos.z * 5))/5) + (cos(fragPos.x * .75) + sin(fragPos.z * .2) + sin(fragPos.y * 2))/10;
    //}
//
//
    //if (height > 8){
    //    groundColor = vec3(0.5, 0.5, 0.5);
    //}
    //if (height > 12){
    //    groundColor = vec3(0.9, 0.9, 0.9);
    //}
    //if (height < 2){
    //    groundColor = vec3(0.5, 0.3, 0.2);
    //}
    //if (height < 1){
    //    groundColor = vec3(0.2, 0.3, 0.9);
    //}

    //vec3 normal = abs(normal);

    float gamma = 2.2;

    vec3 viewDir = vec3(normalize(view_pos - fragPos));

    vec3 result = CalcDirLight(dir_light, normal, viewDir);
    for(int i = 0; i < numPointLights; i++)
        result += CalcPointLight(pointLights[i], normal, fragPos, viewDir);  

    fragColor = vec4(result, 1.0);
    fragColor.rgb = pow(fragColor.rgb, vec3(1.0/gamma));
}