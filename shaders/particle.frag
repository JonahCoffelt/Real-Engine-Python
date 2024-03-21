#version 330 core
out vec4 FragColor;

in vec3 Color;
in vec3 pos;


void main()
{             
    float distance = sqrt(pow(pos.x, 2) + pow(pos.y, 2) + pow(pos.z, 2));
    FragColor = vec4(Color, 1 - distance);
}