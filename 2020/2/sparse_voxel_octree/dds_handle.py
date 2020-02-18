import imageio as ii
from pyffi.formats.dds import DdsFormat


def basic_readwrite():
    data = DdsFormat.Data()

    # read dds
    with open("test_source.dds", "rb") as fp:
        data.read(fp)

    # write dds
    with open("test_dest.dds", "wb") as fp:
        data.write(fp)


def b32_exr_to_dds():
    # img = ii.imread("test_exr_source.exr")
    data = DdsFormat.Data()

    print(data.header.get_size())
    print(data.header.pixel_format.size)

    with open("test_dest.dds", "wb") as fp:
        data.write(fp)


b32_exr_to_dds()
