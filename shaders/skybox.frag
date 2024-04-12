#version 330 core

out vec4 fragColor;

in vec3 clipCoords;

struct star_struct {
    float x;
    float y;
    float s;
};

#define numStars 40
uniform star_struct stars[numStars];
uniform float pitch;
uniform float yaw;

uniform float time;
uniform float FOV;
uniform float aspectRatio;


uniform vec3 color1;
uniform vec3 color2;
uniform vec3 color3;

vec3 moon_color = vec3(150, 150, 250)/255;
vec3 sun_color = vec3(250, 250, 140)/255;


vec3 color;
const float deg2rad = 0.0174533;


void main() {
    float theta = mod((yaw + clipCoords.x * FOV), 360);
    float phi = (pitch + 90 + clipCoords.y * (FOV / aspectRatio));

    float x = sin(phi * deg2rad) * cos(theta * deg2rad);
    float y = cos(phi * deg2rad);
    float z = sin(phi * deg2rad) * sin(theta * deg2rad);

    vec3 sphere_pos = normalize(vec3(x, -y, z));

    float height = sphere_pos.y * cos(clipCoords.x * 50 * deg2rad);
    height += sin(x * 13 + height * 5)/60 + cos(z * 13 - height * 5)/60;

    float moon_sun_side = 180.0;
    if (time > 12.0) {
        moon_sun_side = 0;
    }
    float moon_brightness = min(2.5 / pow(sqrt(pow(phi - abs((time - 12) * 15), 2) + pow(theta - moon_sun_side - 90, 2)), 2), 1.0);
    float sun_brightness = min(2.5 / pow(sqrt(pow(phi + abs((time - 12) * 15) - 180, 2) + pow(theta - (180 - moon_sun_side) - 90, 2)), 2), 1.0);

    float star_brightness = 0.0;
    for (int i = 0; i < numStars; i++) {
        if (abs(phi - stars[i].y) > 2 || abs(theta - stars[i].x) > 2) {continue;}
        star_brightness += min(stars[i].s / pow(sqrt(pow(phi - stars[i].y, 2) + pow(theta - stars[i].x, 2)), 3), .75);
    }

    if (height >= 0){
        color = vec3((color2 - color1) / (0 - 1) * (height - 1) + color1);
    }
    else{
        color = vec3((color3 - color2) / (-1 - 0) * (height - 0) + color2);
    }

    fragColor = vec4(color + vec3(moon_brightness/1.3) * moon_color + vec3(sun_brightness/1.3) * sun_color + vec3(star_brightness) * max(cos(time * 0.261791666667), 0), 1.0);
}