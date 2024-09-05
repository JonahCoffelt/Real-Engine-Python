#version 330 core

layout (location = 0) out vec4 fragColor;

in vec2 uv;
in float shading;
in vec2 textureID;

struct textArray {
    sampler2DArray array;
};

uniform textArray textureArrays[5];


void main() {
    fragColor = texture(textureArrays[int(round(textureID.x))].array, vec3(uv, round(textureID.y)));
    fragColor.rgb *= shading;
}