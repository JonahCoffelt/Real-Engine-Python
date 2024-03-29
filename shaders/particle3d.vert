#version 330 core

layout (location = 0) in vec2 in_texcoord_0;
layout (location = 1) in vec3 in_normal;
layout (location = 2) in vec3 in_position;


in vec3 in_instance_pos;
in vec3 in_instance_color;
in float scale;
in float life;


out vec3 Color;
out vec3 pos;
out vec3 normal;


uniform mat4 m_proj;
uniform mat4 m_view;


void main() {
    pos = in_position;
    Color = in_instance_color;
    normal = abs(in_normal);

    vec3 instance_pos = in_instance_pos;

    float size = scale * life;
    
    mat4 m_model = mat4(
        size, 0.0, 0.0, 0.0,
        0.0, size, 0.0, 0.0,
        0.0, 0.0, size, 0.0,
        instance_pos.x, instance_pos.y, instance_pos.z, 1.0
    );

    gl_Position = m_proj * m_view * m_model * vec4(in_position, 1.0);
}