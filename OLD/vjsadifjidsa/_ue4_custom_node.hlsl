/*
pos
camdir
VTex
*/

const float UNIT = 16.0;
const int NUM_STEPS = 50;

float3 p;

float4 stack = float4(0.0, 0.0, 0.0, 0.0);
float rcpUNIT = 1.0 / UNIT;

for (int i = NUM_STEPS - 1; i > 0; i--)
{
    p = pos + camdir * i;

    float x_offset = p.z % UNIT;
    float y_offset = p.z / UNIT;
    float2 xy = p.xy + float2(x_offset, y_offset);
    xy *= rcpUNIT;

    float4 col = Texture2DSample(VTex, VTexSampler, xy);
    stack += col;
}

return stack / NUM_STEPS;
