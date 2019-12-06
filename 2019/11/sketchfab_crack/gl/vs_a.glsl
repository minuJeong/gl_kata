#version 460

in vec4 Vertex;
out vec4 vViewVertex;

uniform vec3 uQVS;
uniform vec3 uQVT;
uniform vec2 uGlobalTexRatio;
uniform vec2 uGlobalTexSize;
uniform mat4 uProjectionMatrix;
uniform mat4 u_V;
uniform mat4 uModelViewMatrix;
uniform mat4 u_MVP;
uniform vec4 uHalton;
uniform float uDisplay2D;

void main()
{
    vec3 localVertex = Vertex.xyz;
    localVertex += Vertex.w;
    localVertex = localVertex * uQVS * vec3(7.5062659546823e-1, 9.607506508120666e+0, 6.488776727534581e+0).yzx + uQVT;
    vViewVertex = uModelViewMatrix * vec4(localVertex, 1.0);
    mat4 jitteredProjection = uProjectionMatrix;
    jitteredProjection[2].xy += (1.0 - uDisplay2D) * (uHalton.xy * uGlobalTexRatio.xy / uGlobalTexSize.xy);
    gl_Position = jitteredProjection * vViewVertex;

    gl_PointSize = 10.0;
}
