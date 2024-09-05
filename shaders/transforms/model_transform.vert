#version 330 core

layout (location = 0) in vec3 in_position;

layout (location = 1) in vec3 obj_position;
layout (location = 2) in vec3 obj_rotation;
layout (location = 3) in vec3 obj_scale;

out vec3 position;


void main() {
    vec3 rot = obj_rotation;

    mat4 m_rot = mat4(
        cos(rot.z) * cos(rot.y), cos(rot.z) * sin(rot.y) * sin(rot.x) - sin(rot.z) * cos(rot.x), cos(rot.z) * sin(rot.y) * cos(rot.x) + sin(rot.z) * sin(rot.x), 0,
        sin(rot.z) * cos(rot.y), sin(rot.z) * sin(rot.y) * sin(rot.x) + cos(rot.z) * cos(rot.x), sin(rot.z) * sin(rot.y) * cos(rot.x) - cos(rot.z) * sin(rot.x), 0,
        -sin(rot.y)            , cos(rot.y) * sin(rot.x)                                       , cos(rot.y) * cos(rot.x)                                       , 0,
        0                      , 0                                                             , 0                                                             , 1
    );

    mat4 m_trans = mat4(
        1, 0, 0, 0,
        0, 1, 0, 0,
        0, 0, 1, 0,
        obj_position.x, obj_position.y, obj_position.z, 1
    );

    mat4 m_scale = mat4(
        obj_scale.x, 0          , 0          , 0,
        0          , obj_scale.y, 0          , 0,
        0          , 0          , obj_scale.z, 0,
        0          , 0          , 0          , 1
    );

    mat4 m_model = m_trans * m_rot * m_scale;

    position = (m_model * vec4(in_position, 1.0)).xyz;
}