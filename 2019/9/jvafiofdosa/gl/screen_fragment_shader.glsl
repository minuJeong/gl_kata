#version 460

#include ./gl/hg_sdf.glsl

#define EPSILON 0.02
#define FAR 50.0

in vec2 vs_uv;
in vec2 vs_pos;

out vec4 fs_color;

uniform vec2 u_resolution;
uniform float u_time;
uniform vec2 u_input_move;


mat3 look_at_matrix(vec3 o, vec3 t)
{
    vec3 WORLD_UP = vec3(0.0, 1.0, 0.0);
    vec3 FORWARD = normalize(t - o);
    vec3 RIGHT = normalize(cross(FORWARD, WORLD_UP));
    vec3 LOCAL_UP = normalize(cross(RIGHT, FORWARD));
    return mat3(RIGHT, LOCAL_UP, FORWARD);
}

float fArrow(vec3 p, float rad_body, float rad_head, float length_body, float length_head)
{
    float body = fCylinder(p, rad_body, length_body);
    float head = fCone(p - vec3(0.0, length_body, 0.0), rad_head, length_head);
    return min(body, head);
}

float gizmo(vec3 p, vec3 pos, vec3 target)
{
    const float RAD_BODY = 0.015;
    const float RAD_HEAD = 0.06;
    const float LEN_BODY = 0.25;
    const float LEN_HEAD = 0.25;
    
    vec3 center = p - pos;
    center = look_at_matrix(pos, target) * center;

    vec3 px = center - vec3(LEN_BODY, 0.0, 0.0);
    pR(px.xy, -3.1415 * 0.5);
    float arrow_x = fArrow(px, RAD_BODY, RAD_HEAD, LEN_BODY, LEN_HEAD);

    vec3 py = center - vec3(0.0, -LEN_BODY, 0.0);
    pR(py.yz, -3.1415);
    float arrow_y = fArrow(py, RAD_BODY, RAD_HEAD, LEN_BODY, LEN_HEAD);

    vec3 pz = center - vec3(0.0, 0.0, -LEN_BODY);
    pR(pz.yz, -3.1415 * 0.5);
    float arrow_z = fArrow(pz, RAD_BODY, RAD_HEAD, LEN_BODY, LEN_HEAD);

    return min(min(arrow_x, arrow_y), arrow_z);
}

float world(vec3 p, vec3 gizmo_pos)
{
    float d;
    {
        float d_sphere = fSphere(p - vec3(1.2, 0.0, 0.0), 1.77);

        vec3 a = vec3(cos(u_time * 4.2) * 1.2 - 1.3, -1.1, +0.5);
        vec3 b = vec3(sin(u_time * 4.2) * 0.7 - 1.3, +1.5, -0.5);

        float d_disc = fCapsule(p, a, b, 0.8);
        d = fOpUnionRound(d_sphere, d_disc, 0.3);
    }

    {
        float floor = fPlane(p, vec3(0.0, 1.0, 0.0), 10.0);
        d = min(floor, d);
    }

    {
        vec3 box_p = p - vec3(0.5, 0.0, -1.0);
        pR(box_p.xz, u_time);
        float box = fBox(box_p, vec3(0.85 * cos(u_time * 0.5) * 0.5 + 1.2, 0.5, 256.0));

        d = fOpIntersectionStairs(-box, d, 0.75, 3);
    }

    float gizmo = gizmo(p, gizmo_pos, vec3(0.0));
    d = min(d, gizmo);

    return d;
}

float raymarch(vec3 o, vec3 r, vec3 gizmo_pos)
{
    float d, t;
    vec3 p;

    for (int i = 0; i < 48; i++)
    {
        p = o + r * t;
        d = world(p, gizmo_pos);
        if (d < EPSILON || d > FAR)
        {
            break;
        }
        t += d;
    }
    return t;
}

vec3 normal_at(vec3 p, vec3 gizmo_pos)
{
    const vec2 e = vec2(0.01, 0.0);
    return normalize(vec3(
        world(p + e.xyy, gizmo_pos) - world(p - e.xyy, gizmo_pos),
        world(p + e.yxy, gizmo_pos) - world(p - e.yxy, gizmo_pos),
        world(p + e.yyx, gizmo_pos) - world(p - e.yyx, gizmo_pos)
    ));
}

vec3 pointlight_phong(
    vec3 light_color, vec3 light_pos, float radius, float intensity,
    float spec_exponential,
    vec3 P, vec3 N, vec3 V)
{
    // diffuse
    vec3 delta = light_pos - P;
    vec3 L = normalize(delta);
    float distance_sqr = dot(delta, delta) / (radius * radius);
    float diffuse = max(dot(N, L), 0.0) * intensity / distance_sqr;

    // specular
    vec3 H = (normalize(light_pos) + V) * 0.5;
    float specular = pow(max(dot(N, H), 0.0), spec_exponential);
    return diffuse * light_color + specular;
}

vec3 directionallight_lambert(
    vec3 light_color, vec3 light_direction, float intensity,
    vec3 P, vec3 N, vec3 V)
{
    vec3 L = normalize(light_direction);
    vec3 diffuse = max(dot(N, L), 0.0) * light_color * intensity;

    return diffuse;
}

void main()
{
    vec2 uv = vs_uv;
    vec2 pos = vs_pos;

    pos.x *=  u_resolution.x / u_resolution.y;

    vec3 o = vec3(0.0, 0.0, -5.0);
    vec2 rotation = u_input_move.xy;

    vec4 cs_rot = vec4(cos(rotation), sin(rotation));
    o.xz = mat2(cs_rot.x, cs_rot.z, -cs_rot.z, cs_rot.x) * o.xz;
    o.yz = mat2(cs_rot.y, cs_rot.w, -cs_rot.w, cs_rot.y) * o.yz;

    const vec3 LIGHT_POS = vec3(
        cos(u_time * 3.22) * 2.0,
        +1.65,
        -1.65
        // sin(u_time * 3.22) * 2.0
    );

    vec3 r = look_at_matrix(o, vec3(0.0)) * normalize(vec3(pos, 1.0));

    float travel = raymarch(o, r, LIGHT_POS);

    vec3 RGB;
    if (travel < FAR)
    {
        vec3 P = o + r * travel;
        vec3 N = normal_at(P, LIGHT_POS);
        vec3 V = -r;

        // point light

        vec3 lighting;
        lighting += directionallight_lambert(
            vec3(1.0), LIGHT_POS, 0.25,
            P, N, V
        );

        lighting += pointlight_phong(
            vec3(1.0, 1.0, 0.75), LIGHT_POS, 0.5, 3.0,
            64.0,
            P, N, V
        );

        lighting += directionallight_lambert(
            vec3(1.0, 0.0, 1.0), vec3(0.0, -1.0, 0.0), 0.02,
            P, N, V
        );

        // fresnel
        float fresnel = pow(1.0 - max(dot(N, V), 0.0), 5.0);
        lighting += fresnel * vec3(0.04, 0.03, 0.01);

        // ambient
        lighting += vec3(0.05, 0.03, 0.05);

        RGB = lighting;
    }

    fs_color = vec4(RGB, 1.0);
}
