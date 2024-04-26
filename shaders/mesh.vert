#version 330 core

in vec3 in_i_pos0;
in vec3 in_i_pos1;
in vec3 in_i_pos2;
in vec3 in_i_norm;
in vec3 in_i_mat;

out vec3 normal;
out vec3 groundColor;
out vec3 fragPos;
out vec4 shadowCoord;

uniform mat4 m_proj;
uniform mat4 m_view;
uniform mat4 m_view_light;

vec3 position;

mat4 m_shadow_bias = mat4(
    0.5, 0.0, 0.0, 0.0,
    0.0, 0.5, 0.0, 0.0,
    0.0, 0.0, 0.5, 0.0,
    0.5, 0.5, 0.5, 1.0
);

void main() {
    if (gl_VertexID == 0){
        position = in_i_pos0;
    }
    else if (gl_VertexID == 1){
        position = in_i_pos1;
    }
    else {
        position = in_i_pos2;
    }

    gl_Position = m_proj * m_view * vec4(position, 1.0);

    normal = normalize(in_i_norm);
    groundColor = in_i_mat;
    fragPos = position;

    mat4 shadowMVP = m_proj * m_view_light;
    shadowCoord = m_shadow_bias * shadowMVP * vec4(position, 1.0);
    shadowCoord.z -= 0.1;
}