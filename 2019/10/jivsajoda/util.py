
class Loader(object):
    @staticmethod
    def shader(path):
        with open(path, 'r') as fp:
            content = fp.read()

        lines = []
        inc = "#include "
        for line in content.splitlines():
            if line.startswith(inc):
                path = line.split(inc)[1]
                lines.append(Loader.shader(path))

            else:
                lines.append(line)

        return "\n".join(lines)
