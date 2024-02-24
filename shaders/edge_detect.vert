#version 330 core

layout (location = 0) in vec2 in_texcoord_0;
layout (location = 1) in vec3 in_position;

out vec2 TexCoords;

void main()
{
    gl_Position = vec4(in_position.x, in_position.y, 0.0, 1.0); 
    TexCoords = in_texcoord_0;
}  