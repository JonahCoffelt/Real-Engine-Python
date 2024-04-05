#version 330 core

layout (location = 0) in int id;

//in vec3 in_i_norm;
//in vec3 in_v_pos;
//in vec3 in_i_mat;
//
//out vec3 normal;
//out vec3 groundColor;
//out vec3 fragPos;
//out vec4 shadowCoord;
//
//uniform mat4 m_proj;
//uniform mat4 m_view;
//uniform mat4 m_view_light;
//
//mat4 m_shadow_bias = mat4(
//    0.5, 0.0, 0.0, 0.0,
//    0.0, 0.5, 0.0, 0.0,
//    0.0, 0.0, 0.5, 0.0,
//    0.5, 0.5, 0.5, 1.0
//);
//
//void main() {
//    gl_Position = m_proj * m_view * vec4(in_v_pos, 1.0);
//    normal = normalize(in_i_norm);
//
//    groundColor = in_i_mat;
//    fragPos = in_v_pos;
//
//    mat4 shadowMVP = m_proj * m_view_light;
//    shadowCoord = m_shadow_bias * shadowMVP * vec4(in_v_pos, 1.0);
//    shadowCoord.z -= 0.0005;
//}


in vec3 in_i_norm0;
in vec3 in_i_pos0;
in vec3 in_i_norm1;
in vec3 in_i_pos1;
in vec3 in_i_norm2;
in vec3 in_i_pos2;
in vec3 in_i_mat0;


vec3 position;
vec3 norm;
vec3 material;

out vec3 normal;
out vec3 groundColor;
out vec3 fragPos;
out vec4 shadowCoord;

uniform mat4 m_proj;
uniform mat4 m_view;
uniform mat4 m_view_light;

mat4 m_shadow_bias = mat4(
    0.5, 0.0, 0.0, 0.0,
    0.0, 0.5, 0.0, 0.0,
    0.0, 0.0, 0.5, 0.0,
    0.5, 0.5, 0.5, 1.0
);

void main() {
    if (id == 0){
        norm = in_i_norm0;
        position = in_i_pos0;
    }
    else if (id == 1){
        norm = in_i_norm1;
        position = in_i_pos1;
    }
    else {
        norm = in_i_norm2;
        position = in_i_pos2;
    }

    gl_Position = m_proj * m_view * vec4(position, 1.0);

    normal = normalize(norm);
    groundColor = in_i_mat0;
    fragPos = position;

    mat4 shadowMVP = m_proj * m_view_light;
    shadowCoord = m_shadow_bias * shadowMVP * vec4(position, 1.0);
    shadowCoord.z -= 0.0005;
}