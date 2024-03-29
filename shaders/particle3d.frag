#version 330 core
out vec4 FragColor;

in vec3 Color;
in vec3 normal;
in vec3 pos;


void main()
{             
    float diff = max(dot(normal, vec3(1, 1, 1)), 0.0) / 2;
    FragColor = vec4(Color * (vec3(.25) + vec3(diff)) + vec3(.2), 1.0);
}