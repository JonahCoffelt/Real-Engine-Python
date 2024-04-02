#version 330 core

layout (triangles) in;
layout (triangle_strip, max_vertices = 3) out;

in DATA{
    vec3 normal;
    vec3 groundColor;
    vec3 fragPos;
    vec4 shadowCoord;
} data_in[];

uniform mat4 m_proj;
uniform mat4 m_view;

out vec3 normal;
out vec3 groundColor;
out vec3 fragPos;
out vec4 shadowCoord;

void main() {
    gl_Position = m_proj * m_view * gl_in[0].gl_Position;
    normal = data_in[0].normal;
    groundColor = data_in[0].groundColor;
    fragPos = data_in[0].fragPos;
    shadowCoord = data_in[0].shadowCoord;
    EmitVertex();
    gl_Position = m_proj * m_view * gl_in[1].gl_Position;
    normal = data_in[1].normal;
    groundColor = data_in[1].groundColor;
    fragPos = data_in[1].fragPos;
    shadowCoord = data_in[1].shadowCoord;
    EmitVertex();
    gl_Position = m_proj * m_view * gl_in[2].gl_Position;
    normal = data_in[2].normal;
    groundColor = data_in[2].groundColor;
    fragPos = data_in[2].fragPos;
    shadowCoord = data_in[2].shadowCoord;
    EmitVertex();

    EndPrimitive();

    //gl_Position = m_proj * m_view * gl_in[0].gl_Position;
    //normal = data_in[0].normal;
    //groundColor = data_in[0].groundColor;
    //fragPos = data_in[0].fragPos;
    //shadowCoord = data_in[0].shadowCoord;
    //EmitVertex();
//
    //gl_Position = m_proj * m_view * gl_in[1].gl_Position;
    //normal = data_in[1].normal;
    //groundColor = data_in[1].groundColor;
    //fragPos = data_in[1].fragPos;
    //shadowCoord = data_in[1].shadowCoord;
    //EmitVertex();
//
    //gl_Position = m_proj * m_view * gl_in[2].gl_Position;
    //normal = data_in[2].normal;
    //groundColor = data_in[2].groundColor;
    //fragPos = data_in[2].fragPos;
    //shadowCoord = data_in[2].shadowCoord;
    //EmitVertex();
//
    //EndPrimitive();
}  

