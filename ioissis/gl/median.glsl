#version 460

layout(local_size_x=8, local_size_y=8) in;

layout(binding=0) buffer bind_0
{
    vec4 data_0[];
};

layout(binding=1) buffer bind_1
{
    vec4 data_1[];
};

uniform uint u_width;
uniform uint u_height;

// window size
const int RADIUS = 2;
const int WIDHEG = 25;
const int MEDIAN = 12;


float luminance(vec3 rgb)
{
    return rgb.x * 0.213 + rgb.y * 0.715 + rgb.z * 0.072;
}

float luminance(vec4 rgba)
{
    vec3 rgb = rgba.xyz;
    return luminance(rgb);
}

uint i_at_xy(uvec2 xy)
{
    xy.x = clamp(xy.x, 0, u_width);
    xy.y = clamp(xy.y, 0, u_height);
    return xy.x + xy.y * u_width;
}

void main()
{
    uvec2 xy = gl_LocalInvocationID.xy + gl_WorkGroupID.xy * uvec2(8, 8);
    uvec2 wh = uvec2(u_width, u_height);
    uint i = i_at_xy(xy);
    vec4 window[WIDHEG];

    ivec2 ixy = ivec2(xy);

    // convolutional window
    for (int xx = -RADIUS; xx <= RADIUS; xx++)
    {
        uint x = uint(ixy.x + xx);
        x = min(x, u_width - 1);

        for (int yy = -RADIUS; yy <= RADIUS; yy++)
        {
            uint y = uint(ixy.y + yy);
            y = min(y, u_height - 1);

            uint cursor = i_at_xy(uvec2(x, y));
            window[cursor] = vec4(data_0[cursor]);
        }
    }

    // sort
    for (int i = 0; i < WIDHEG; i++)
    {
        vec4 a = window[i + 0];
        vec4 b = window[i + 1];

        if (luminance(a) > luminance(b))
        {
            window[i + 0] = b;
            window[i + 1] = a;
        }
    }

    vec4 median_value = window[MEDIAN];
    median_value.a = 1.0;
    data_1[i] = median_value;

    vec2 uv = vec2(xy) / vec2(wh);

    float b = data_0[i].x;
    for (int j = int(i - 10); j < int(i + 10); j++)
    {
        float jb = data_0[j].x;
        if (b < jb)
        {
            b = jb;
        }
    }

    data_1[i] = vec4(0.0, 0.0, b, 1.0);
}
