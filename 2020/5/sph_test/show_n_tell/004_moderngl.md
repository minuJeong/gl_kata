ModernGL
===

python binding for OpenGL

simplest example of using moderngl

```
import moderngl

gl = moderngl.create_context()
program = gl.program(...)
vertex_array = gl.vertex_array(program, [(vertices, vertex_layout, attributes)], indices)
vertex_array.render()
```


You can be more creative.

render without geometry but issuing 1000 vertex program,
and procedurally generates vertices using "gl_VertexID"

```
vertex_array = gl.vertex_array(program, [])
vertex_array.render(vertices=1000)
```

or very easy to use instanced rendering with "gl_InstanceID"

```
vertex_array.render(instances=1000)
vertex_array.render(instances=[list_of_mat4(numpy_array or glm::mat4)])
```
