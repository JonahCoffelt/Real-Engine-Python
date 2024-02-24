#version 330 core

layout (location = 0) in vec3 in_position;

out vec3 texCubeCoords;
out float height;

uniform mat4 m_proj;
uniform mat4 m_view_sky;

void main() {
    texCubeCoords = in_position;
    vec4 pos = m_proj * m_view_sky * vec4(in_position, 1.0);
    gl_Position = pos.xyww;
    gl_Position.z -= 0.0001;

    height = in_position.y;
}