#version 330 core
out vec4 FragColor;

in vec3 Color;
in vec3 pos;

float clampSDF(float value) {
    if (value > 0.0){
        value = 0.0;
    }
    else{
        value = -1.0;
    }
    return value;
}


float sdCircle( vec2 p, float s )
{
  return length(p)-s;
}


float sdBox( in vec2 p, in vec2 b )
{
    vec2 d = abs(p)-b;
    return length(max(d,0.0)) + min(max(d.x,d.y),0.0);
}


float sdEquilateralTriangle( in vec2 p, in float r )
{
    const float k = sqrt(3.0);
    p.x = abs(p.x) - r;
    p.y = p.y + r/k;
    if( p.x+k*p.y>0.0 ) p = vec2(p.x-k*p.y,-k*p.x-p.y)/2.0;
    p.x -= clamp( p.x, -2.0*r, 0.0 );
    return -length(p)*sign(p.y);
}


void main()
{             
    float distance = sdCircle(vec2(pos.x, pos.y), 1);
    //float distance = clampSDF(sdCircle(vec2(pos.x, pos.y), .5));
    //float distance = clampSDF(sdBox(vec2(pos.x, pos.y), vec2(.5)));
    //float distance = clampSDF(sdEquilateralTriangle(vec2(pos.x, pos.y), .5));
    //float distance = sdEquilateralTriangle(vec2(pos.x, pos.y), 1);
    //float distance = clampSDF(sdHexagram(vec2(pos.x, pos.y), .5));
    //float distance = clampSDF(sdMoon(vec2(pos.x, pos.y), .5, 1, .75));

    FragColor = vec4(Color, -distance);
}