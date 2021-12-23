filegroup(
    name = "packer",
    srcs = [
        "linux/asset_packer",
    ],
    visibility = ["//visibility:public"],
)

filegroup(
    name = "unpacker",
    srcs = [
        "linux/asset_unpacker",
    ],
    visibility = ["//visibility:public"],
)

filegroup(
    name = "packed",
    srcs = [
        "assets/packed.pak"
    ],
    visibility = ["//visibility:public"],
)

exports_files([
    "linux/starbound",
    "linux/starbound_server",
])

genrule(
    name = "unpacked",
    srcs = [
        ":unpacker",
        ":packed"
    ],
    outs = [
        "core_assets",
    ],
    cmd = "$(location :unpacker) $(location :packed) $@",
    visibility = ["//visibility:public"],
)

genrule(
    name = "game",
    srcs = [
        "linux/starbound",
        "linux/libsteam_api.so"
    ],
    executable = True,
    outs = ["run_game.sh"],
    cmd = "echo command $$(realpath $(location linux/starbound) ) >$@"
)
