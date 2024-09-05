#version 330 core

layout (location = 0) in vec3 in_position;
layout (location = 1) in vec2 in_uv;
layout (location = 2) in vec3 in_normal;

uniform mat4 m_proj;
uniform mat4 m_view;
uniform mat4 m_model;

out vec2 uv;
out float shading;

void main() {
    uv = in_uv;
    vec3 normal = normalize(mat3(transpose(inverse(m_model))) * in_normal);  
    shading = ((dot(vec3(.5, .25, .75), normal) + 1) / 2) * .75 + .25;
    gl_Position = m_proj * m_view * m_model * vec4(in_position, 1.0);
}