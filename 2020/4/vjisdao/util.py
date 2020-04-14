
def mat4_to_tuple(m):
    output = []
    for row in m:
        for col in row:
            output.append(col)
    return tuple(output)
