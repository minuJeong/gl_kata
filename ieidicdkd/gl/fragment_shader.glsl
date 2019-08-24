#version 460

#define NEAR 0.002
#define FAR 10.0

in vec2 vs_pos;
in vec2 vs_uv;

out vec4 fs_color;


float world(vec3 p)
{
    return length(p) - 2.0;
}

float raymarch(vec3 o, vec3 r, out float perf_counter)
{
    vec3 p;
    float d;
    float t;

    for (int i = 0; i < 128; i++)
    {
        perf_counter++;

        p = o + r * t;
        d = world(p);
        if (d < NEAR || t > FAR)
        {
            break;
        }
        t += d;
    }

    return t;
}

void main()
{
    vec3 o = vec3(0.0, 0.0, -5.0);
    vec3 r = normalize(vec3(vs_pos, 1.0));

    float perf_counter;
    float t = raymarch(o, r, perf_counter);
    vec3 rgb = vec3(t / FAR);

    rgb = (perf_counter / 128.0).xxx;

    fs_color = vec4(rgb, 1.0);
}
