#version 330 core

layout (location = 0) out vec4 fragColor;


in vec3 normal;


void main() {
    fragColor = vec4(abs(normal), 1.0);
}