import ctypes as ct


class ENUM(object):
    def __init__(self, id):
        super(ENUM, self).__init__()
        type(self).parse(id)

    @classmethod
    def parse(cls, idx):
        for k, v in vars(cls).items():
            if k.startswith("__"):
                continue
            if v == idx:
                return k
        raise Exception(f"idx not found: {idx}")


class HAPI_PackedPrimInstancingMode(ENUM):
    HAPI_PACKEDPRIM_INSTANCING_MODE_INVALID = -1
    HAPI_PACKEDPRIM_INSTANCING_MODE_DISABLED = 0
    HAPI_PACKEDPRIM_INSTANCING_MODE_HIERARCHY = 1
    HAPI_PACKEDPRIM_INSTANCING_MODE_FLAT = 2
    HAPI_PACKEDPRIM_INSTANCING_MODE_MAX = 3


class HAPI_SessionType(ENUM):
    HAPI_SESSION_INPROCESS = 0
    HAPI_SESSION_THRIFT = 1
    HAPI_SESSION_CUSTOM1 = 2
    HAPI_SESSION_CUSTOM2 = 3
    HAPI_SESSION_CUSTOM3 = 4
    HAPI_SESSION_MA = 5


class HAPI_Result(ENUM):
    HAPI_RESULT_SUCCESS = 0
    HAPI_RESULT_FAILURE = 1
    HAPI_RESULT_ALREADY_INITIALIZED = 2
    HAPI_RESULT_NOT_INITIALIZED = 3
    HAPI_RESULT_CANT_LOADFILE = 4
    HAPI_RESULT_PARM_SET_FAILED = 5
    HAPI_RESULT_INVALID_ARGUMENT = 6
    HAPI_RESULT_CANT_LOAD_GEO = 7
    HAPI_RESULT_CANT_GENERATE_PRESET = 8
    HAPI_RESULT_CANT_LOAD_PRESET = 9
    HAPI_RESULT_ASSET_DEF_ALREADY_LOADED = 10
    HAPI_RESULT_NO_LICENSE_FOUND = 110
    HAPI_RESULT_DISALLOWED_NC_LICENSE_FOUND = 120
    HAPI_RESULT_DISALLOWED_NC_ASSET_WITH_C_LICENSE = 130
    HAPI_RESULT_DISALLOWED_NC_ASSET_WITH_LC_LICENSE = 140
    HAPI_RESULT_DISALLOWED_LC_ASSET_WITH_C_LICENSE = 150
    HAPI_RESULT_DISALLOWED_HENGINEINDIE_W_3PARTY_PLUGIN = 160
    HAPI_RESULT_ASSET_INVALID = 200
    HAPI_RESULT_NODE_INVALID = 210
    HAPI_RESULT_USER_INTERRUPTED = 300
    HAPI_RESULT_INVALID_SESSION = 400


class HAPI_Session(ct.Structure):
    _field_ = [("type", HAPI_SessionType.HAPI_SESSION_INPROCESS, 4), ("id", 0, 4)]


class HAPI_CookOptions(ct.Structure):
    splitGeosByGroup = False
    maxVerticesPerPrimitive = 0
    refineCurveToLinear = False
    curveRefineLOD = 0.0
    clearErrorsAndWarnings = False
    cookTemplatedGeos = False
    splitPointsByVertexAttributes = False
    packedPrimInstancingMode = False
    handleBoxPartTypes = False
    handleSpherePartTypes = False
    extraFlags = 0


hapi_dllpath = "libHAPI.dll"
hapi = ct.WinDLL(hapi_dllpath)

session = ct.byref(HAPI_Session())
cook_options = ct.byref(HAPI_CookOptions())

session_create_res = hapi.HAPI_CreateInProcessSession(session)
print("create session response: ", HAPI_Result.parse(session_create_res))

res = hapi.HAPI_Initialize(session, cook_options, True, 10, "", "./", "./", "./", "./")
print("initialize response: ", HAPI_Result.parse(res))

res = hapi.HAPI_IsInitialized(session)
print("is_initialized response", HAPI_Result.parse(res))

node_id_0 = ct.c_int32(1)
node_id_1 = ct.c_int32(2)
node_id_2 = ct.c_int32(3)
res = hapi.HAPI_CreateNode(
    session, -1, "geo", "hello_houdini_0", True, ct.byref(node_id_0)
)
print("create_node response", HAPI_Result.parse(res), f"id: {node_id_0}")
res = hapi.HAPI_CreateNode(
    session, ct.byref(node_id_0), "hello", "hello_houdini_1", True, ct.byref(node_id_1)
)
print("create_node response", HAPI_Result.parse(res), f"id: {node_id_1}")
res = hapi.HAPI_CreateNode(
    session,
    ct.byref(node_id_1),
    "Object/",
    "hello_houdini_2",
    True,
    ct.byref(node_id_2),
)
print("create_node response", HAPI_Result.parse(res), f"id: {node_id_2}")

print(node_id_0, node_id_1, node_id_2)

cooking_total_count = ct.c_int(0)
res = hapi.HAPI_GetCookingTotalCount(session, ct.byref(cooking_total_count))
print("get_cooking_total_count response", HAPI_Result.parse(res))
print(cooking_total_count)
