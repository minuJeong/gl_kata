#version 460
layout(local_size_x=8) in;

uniform float u_time;
uniform float u_count;

layout(binding=0) buffer audio_buffer
{
    float data[];
};

const float OFFSET = 1136;

void main()
{
    uint ID = gl_LocalInvocationID.x + gl_WorkGroupID.x * gl_WorkGroupSize.x;

    float x = float(ID + OFFSET * u_count) / 1248.0;
    float y = 0.0;

    for (float i = 0.0; i < 10.0; i++)
    {
        y += cos(x * (i * 20.3)) * 0.03;
    }

    data[ID] = y;
}
