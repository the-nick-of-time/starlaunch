load("@bazel_tools//tools/build_defs/repo:http.bzl", "http_archive")

http_archive(
    name = "starbound",
    build_file = "//dependencies:starbound.BUILD",
    sha256 = "9a571b799aa2d8be7f1d6c7fb20b3c8fe36e6cc58cab4e831cca64ae843144f4",
    strip_prefix = "starbound_1.4.4_linux",
    type = "zip",
    urls = [
        "http://localhost/starbound_1.4.4_linux.zip",
        "https://dl.humble.com/chucklefish/starbound_1.4.4_linux.zip?gamekey=bv5He8GR3z4H&ttl=1639973219&t=fc47b73bd0a1d1f0a069932bc05e7f02",
    ],
)

http_archive(
    name = "rules_python",
    sha256 = "b6d46438523a3ec0f3cead544190ee13223a52f6a6765a29eae7b7cc24cc83a0",
    url = "https://github.com/bazelbuild/rules_python/releases/download/0.1.0/rules_python-0.1.0.tar.gz",
)
