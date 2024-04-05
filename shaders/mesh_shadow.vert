#version 330 core

layout (location = 0) in int id;

in vec3 in_i_pos0;
in vec3 in_i_pos1;
in vec3 in_i_pos2;


uniform mat4 m_proj;
uniform mat4 m_view_light;
uniform mat4 m_model;


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
    mat4 mvp = m_proj * m_view_light;
    gl_Position = mvp * vec4(position, 1.0);
}