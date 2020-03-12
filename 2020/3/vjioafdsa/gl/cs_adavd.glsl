// --
#version 460

#define SURFACE 0.002
#define FAR 100.0

const vec3 ZERO = vec3(0.0, 0.0, 0.0);
const vec3 UP = vec3(0.0, 1.0, 0.0);

layout(local_size_x=8, local_size_y=8) in;

layout(binding=0) buffer tex_out
{
    vec4 colour[];
};

uniform uvec2 u_res = uvec2(1, 1);
uniform int u_frame = 0;

float time()
{
    return float(u_frame) * 0.1;
}


float sdf_sphere(vec3 pos, float rad) { return length(pos) - rad; }

float sdf_world(vec3 pos)
{
    float t = time();
    float d = FAR;
    {
        vec3 q = pos;
        q.x += cos(t) * 0.6;

        float radius = 2.2;
        float d_sphere = sdf_sphere(q, radius);

        d = min(d, d_sphere);
    }
    return d;
}

float march(vec3 origin, vec3 ray)
{
    vec3 pos;
    float travel = 0.2, distance;
    for (float step = 0.0; step < 128.0; step += 1.0)
    {
        pos = origin + ray * travel;
        distance = sdf_world(pos);
        if (distance < SURFACE || travel > FAR) { break; }
        travel += distance;
    }
    return travel;
}

mat3 lookat(vec3 p, vec3 at, vec3 up)
{
    vec3 f = normalize(at - p);
    vec3 r = cross(f, up);
    vec3 u = cross(r, f);
    return mat3(r, u, f);
}

vec3 normalat(vec3 p)
{
    const vec2 e = vec2(0.002, 0.0);
    return normalize(sdf_world(p) - vec3(
        sdf_world(p - e.xyy),
        sdf_world(p - e.yxy),
        sdf_world(p - e.yyx)
    ));
}

vec3 render(vec2 uv)
{
    vec3 rgb = vec3(0.0, 0.2, 0.2);

    vec3 campos = vec3(-2.0, 3.0, -5.0);
    vec3 camdir = lookat(campos, ZERO, UP) * normalize(vec3(uv * 2.0 - 1.0, 1.0));
    float travel = march(campos, camdir);

    if (travel < FAR)
    {
        vec3 P = campos + camdir * travel;
        vec3 N = normalat(P);

        rgb = N;
    }

    return rgb;
}

void main()
{
    uvec2 xy = gl_LocalInvocationID.xy + gl_WorkGroupID.xy * gl_WorkGroupSize.xy;
    vec2 uv = vec2(xy) / u_res;

    vec3 rgb = render(uv);

    uint i = xy.x + xy.y * u_res.x;
    colour[i] = vec4(rgb, 1.0);
}
