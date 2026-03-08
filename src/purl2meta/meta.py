# -*- coding: utf-8 -*-
#
# Copyright (c) the purl authors
# SPDX-License-Identifier: MIT
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from packageurl import PackageURL
from packageurl.contrib.purl2url import DEFAULT_MAVEN_REPOSITORY
from packageurl.contrib.purl2url import escape_golang_path
from packageurl.contrib.route import NoRouteAvailable
from packageurl.contrib.route import Router

metadata_router = Router()


def get_metadata_url(purl):
    """
    Return a metadata API URL inferred from the `purl` string.
    """
    if purl:
        try:
            return metadata_router.process(purl)
        except NoRouteAvailable:
            return


def get_metadata(purl):
    """
    Fetch and return metadata from the registry API. Requires httpx.
    """
    try:
        import httpx
    except ImportError:
        raise ImportError(
            "httpx is required for fetching metadata. "
            "Install it with: pip install purl2meta[fetch]"
        )

    url = get_metadata_url(purl)
    if not url:
        return

    headers = {
        "Accept": "application/json",
        "User-Agent": "purl2meta",
    }

    response = httpx.get(url, headers=headers, timeout=30, follow_redirects=True)
    response.raise_for_status()

    content_type = response.headers.get("content-type", "")
    if "json" in content_type:
        return response.json()
    return response.text


@metadata_router.route("pkg:npm/.*")
def build_npm_metadata_url(purl):
    purl_data = PackageURL.from_string(purl)
    namespace = purl_data.namespace
    name = purl_data.name
    version = purl_data.version

    if not name:
        return

    base_url = "https://registry.npmjs.org/"
    if namespace:
        base_url += f"{namespace}/"
    base_url += name

    if version:
        base_url += f"/{version}"

    return base_url


@metadata_router.route("pkg:pypi/.*")
def build_pypi_metadata_url(purl):
    purl_data = PackageURL.from_string(purl)
    name = (purl_data.name or "").replace("_", "-")
    version = purl_data.version

    if not name:
        return

    if version:
        return f"https://pypi.org/pypi/{name}/{version}/json"
    return f"https://pypi.org/pypi/{name}/json"


@metadata_router.route("pkg:cargo/.*")
def build_cargo_metadata_url(purl):
    purl_data = PackageURL.from_string(purl)
    name = purl_data.name
    version = purl_data.version

    if not name:
        return

    if version:
        return f"https://crates.io/api/v1/crates/{name}/{version}"
    return f"https://crates.io/api/v1/crates/{name}"


@metadata_router.route("pkg:(gem|rubygems)/.*")
def build_rubygems_metadata_url(purl):
    purl_data = PackageURL.from_string(purl)
    name = purl_data.name
    version = purl_data.version

    if not name:
        return

    if version:
        return f"https://rubygems.org/api/v2/rubygems/{name}/versions/{version}.json"
    return f"https://rubygems.org/api/v1/gems/{name}.json"


@metadata_router.route("pkg:nuget/.*")
def build_nuget_metadata_url(purl):
    purl_data = PackageURL.from_string(purl)
    name = purl_data.name
    version = purl_data.version

    if not name:
        return

    name_lower = name.lower()

    if version:
        return f"https://api.nuget.org/v3/registration5-semver1/{name_lower}/{version}.json"
    return f"https://api.nuget.org/v3/registration5-semver1/{name_lower}/index.json"


@metadata_router.route("pkg:hex/.*")
def build_hex_metadata_url(purl):
    purl_data = PackageURL.from_string(purl)
    name = purl_data.name
    version = purl_data.version

    if not name:
        return

    if version:
        return f"https://hex.pm/api/packages/{name}/releases/{version}"
    return f"https://hex.pm/api/packages/{name}"


@metadata_router.route("pkg:pub/.*")
def build_pub_metadata_url(purl):
    purl_data = PackageURL.from_string(purl)
    name = purl_data.name

    if not name:
        return

    return f"https://pub.dev/api/packages/{name}"


@metadata_router.route("pkg:hackage/.*")
def build_hackage_metadata_url(purl):
    purl_data = PackageURL.from_string(purl)
    name = purl_data.name
    version = purl_data.version

    if not name:
        return

    if version:
        return f"https://hackage.haskell.org/package/{name}-{version}/{name}.cabal"
    return f"https://hackage.haskell.org/package/{name}.json"


@metadata_router.route("pkg:golang/.*")
def build_golang_metadata_url(purl):
    purl_data = PackageURL.from_string(purl)
    namespace = purl_data.namespace
    name = purl_data.name
    version = purl_data.version

    if not name:
        return

    if namespace:
        name = f"{namespace}/{name}"

    escaped_name = escape_golang_path(name)

    if version:
        escaped_version = escape_golang_path(version)
        if not escaped_version.startswith("v"):
            escaped_version = "v" + escaped_version
        return f"https://proxy.golang.org/{escaped_name}/@v/{escaped_version}.info"
    return f"https://proxy.golang.org/{escaped_name}/@v/list"


@metadata_router.route("pkg:maven/.*")
def build_maven_metadata_url(purl):
    purl_data = PackageURL.from_string(purl)
    namespace = purl_data.namespace
    name = purl_data.name
    version = purl_data.version
    qualifiers = purl_data.qualifiers

    if not (namespace and name):
        return

    base_url = qualifiers.get("repository_url", DEFAULT_MAVEN_REPOSITORY)
    ns_path = namespace.replace(".", "/")

    if version:
        return f"{base_url}/{ns_path}/{name}/{version}/{name}-{version}.pom"
    return f"{base_url}/{ns_path}/{name}/maven-metadata.xml"


@metadata_router.route("pkg:composer/.*")
def build_composer_metadata_url(purl):
    purl_data = PackageURL.from_string(purl)
    namespace = purl_data.namespace
    name = purl_data.name

    if not (namespace and name):
        return

    return f"https://repo.packagist.org/p2/{namespace}/{name}.json"


@metadata_router.route("pkg:cocoapods/.*")
def build_cocoapods_metadata_url(purl):
    purl_data = PackageURL.from_string(purl)
    name = purl_data.name

    if not name:
        return

    return f"https://trunk.cocoapods.org/api/v1/pods/{name}"


@metadata_router.route("pkg:conda/.*")
def build_conda_metadata_url(purl):
    purl_data = PackageURL.from_string(purl)
    name = purl_data.name
    qualifiers = purl_data.qualifiers or {}

    if not name:
        return

    channel = qualifiers.get("channel", "main")
    return f"https://api.anaconda.org/package/{channel}/{name}"


@metadata_router.route("pkg:github/.*")
def build_github_metadata_url(purl):
    purl_data = PackageURL.from_string(purl)
    namespace = purl_data.namespace
    name = purl_data.name
    version = purl_data.version

    if not (namespace and name):
        return

    if version:
        return f"https://api.github.com/repos/{namespace}/{name}/releases/tags/{version}"
    return f"https://api.github.com/repos/{namespace}/{name}"


@metadata_router.route("pkg:gitlab/.*")
def build_gitlab_metadata_url(purl):
    purl_data = PackageURL.from_string(purl)
    namespace = purl_data.namespace
    name = purl_data.name
    version = purl_data.version

    if not (namespace and name):
        return

    encoded_path = f"{namespace}%2F{name}"

    if version:
        return f"https://gitlab.com/api/v4/projects/{encoded_path}/releases/{version}"
    return f"https://gitlab.com/api/v4/projects/{encoded_path}"


@metadata_router.route("pkg:bitbucket/.*")
def build_bitbucket_metadata_url(purl):
    purl_data = PackageURL.from_string(purl)
    namespace = purl_data.namespace
    name = purl_data.name

    if not (namespace and name):
        return

    return f"https://api.bitbucket.org/2.0/repositories/{namespace}/{name}"


@metadata_router.route("pkg:cran/.*")
def build_cran_metadata_url(purl):
    purl_data = PackageURL.from_string(purl)
    name = purl_data.name
    version = purl_data.version

    if not name:
        return

    if version:
        return f"https://crandb.r-pkg.org/{name}/{version}"
    return f"https://crandb.r-pkg.org/{name}"
