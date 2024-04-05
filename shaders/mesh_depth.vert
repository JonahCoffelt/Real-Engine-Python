#version 330 core

layout (location = 0) in int id;

in vec3 in_i_pos0;
in vec3 in_i_pos1;
in vec3 in_i_pos2;

uniform mat4 m_proj;
uniform mat4 m_view;

vec3 position;

void main() {
    if (id == 0){
        position = in_i_pos0;
    }
    else if (id == 1){
        position = in_i_pos1;
    }
    else {
        position = in_i_pos2;
    }

    gl_Position = m_proj * m_view * vec4(position, 1.0);
}