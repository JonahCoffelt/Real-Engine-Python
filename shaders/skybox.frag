#version 330 core

out vec4 fragColor;

in vec3 texCubeCoords;
in float height;

uniform samplerCube u_texture_skybox;
uniform float time;

vec3 night_difference = vec3(.7, .65, .5);

void main() {
    fragColor = texture(u_texture_skybox, texCubeCoords);
    fragColor.rgb -= night_difference * (min(.75, max(.25, (sin(time / 500)*.5 + .5))) * 2 - .5);
}