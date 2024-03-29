#version 330 core

layout (location = 0) in vec3 in_position;

in vec3 in_instance_pos;
in vec3 in_instance_color;
in float scale;
in float life;


out vec3 Color;
out vec3 pos;

uniform mat4 m_proj;
uniform mat4 m_view;
uniform vec3 cam;

void main() {
    pos = in_position;
    Color = in_instance_color;

    vec3 instance_pos = in_instance_pos;
    
    float yaw = -atan(instance_pos.x - cam.x, instance_pos.z - cam.z);
    float pitch = atan(instance_pos.y - cam.y, sqrt(pow(instance_pos.x - cam.x, 2) + pow(instance_pos.z - cam.z, 2)));
    float size = scale * life;

    mat4 m_model = mat4(
       size, 0.0, 0.0, 0.0,
        0.0, size, 0.0, 0.0,
        0.0, 0.0, size, 0.0,
        instance_pos.x, instance_pos.y, instance_pos.z, 1.0
    );

    mat4 y_rot = mat4(
        cos(yaw), 0.0, sin(yaw), 0.0,
        0.0, 1.0, 0.0, 0.0,
        -sin(yaw), 0.0, cos(yaw), 0.0,
        0.0, 0.0, 0.0, 1.0
    );

    mat4 x_rot = mat4(
        1.0, 0.0, 0.0, 0.0,
        0.0, cos(pitch), -sin(pitch), 0.0,
        0, sin(pitch), cos(pitch), 0.0,
        0.0, 0.0, 0.0, 1.0
    );

    m_model = m_model * y_rot * x_rot;

    gl_Position = m_proj * m_view * m_model * vec4(in_position, 1.0);
}