# -*- coding: utf-8 -*-
#
# Copyright (c) the purl authors
# SPDX-License-Identifier: MIT

from unittest.mock import MagicMock
from unittest.mock import patch

import pytest

from purl2meta import get_metadata_url, get_metadata


def test_get_metadata_url():
    purls_url = {
        # npm — basic, scoped, scoped percent-encoded, no version
        "pkg:npm/express@4.18.2": "https://registry.npmjs.org/express/4.18.2",
        "pkg:npm/express": "https://registry.npmjs.org/express",
        "pkg:npm/@babel/core@7.20.0": "https://registry.npmjs.org/@babel/core/7.20.0",
        "pkg:npm/%40babel/core@7.20.0": "https://registry.npmjs.org/@babel/core/7.20.0",
        "pkg:npm/lodash@4.17.21": "https://registry.npmjs.org/lodash/4.17.21",
        "pkg:npm/@types/node@20.11.0": "https://registry.npmjs.org/@types/node/20.11.0",
        "pkg:npm/@angular/core@17.0.0": "https://registry.npmjs.org/@angular/core/17.0.0",
        "pkg:npm/left-pad": "https://registry.npmjs.org/left-pad",
        # pypi — underscore normalization, hyphenated names, no version
        "pkg:pypi/requests@2.28.0": "https://pypi.org/pypi/requests/2.28.0/json",
        "pkg:pypi/requests": "https://pypi.org/pypi/requests/json",
        "pkg:pypi/packageurl_python@0.11.0": "https://pypi.org/pypi/packageurl-python/0.11.0/json",
        "pkg:pypi/Django@4.2.7": "https://pypi.org/pypi/django/4.2.7/json",
        "pkg:pypi/black": "https://pypi.org/pypi/black/json",
        "pkg:pypi/scikit_learn@1.3.2": "https://pypi.org/pypi/scikit-learn/1.3.2/json",
        "pkg:pypi/Pillow@10.1.0": "https://pypi.org/pypi/pillow/10.1.0/json",
        # cargo — with and without version
        "pkg:cargo/rand@0.7.2": "https://crates.io/api/v1/crates/rand/0.7.2",
        "pkg:cargo/rand": "https://crates.io/api/v1/crates/rand",
        "pkg:cargo/serde@1.0.193": "https://crates.io/api/v1/crates/serde/1.0.193",
        "pkg:cargo/tokio@1.35.0": "https://crates.io/api/v1/crates/tokio/1.35.0",
        "pkg:cargo/clap": "https://crates.io/api/v1/crates/clap",
        # gem/rubygems — both type aliases, with and without version
        "pkg:gem/bundler@2.3.23": "https://rubygems.org/api/v2/rubygems/bundler/versions/2.3.23.json",
        "pkg:rubygems/bundler": "https://rubygems.org/api/v1/gems/bundler.json",
        "pkg:gem/rails": "https://rubygems.org/api/v1/gems/rails.json",
        "pkg:gem/nokogiri@1.15.4": "https://rubygems.org/api/v2/rubygems/nokogiri/versions/1.15.4.json",
        "pkg:rubygems/sinatra@3.1.0": "https://rubygems.org/api/v2/rubygems/sinatra/versions/3.1.0.json",
        "pkg:rubygems/devise": "https://rubygems.org/api/v1/gems/devise.json",
        # nuget — case-insensitive name lowering
        "pkg:nuget/System.Text.Json@6.0.6": "https://api.nuget.org/v3/registration5-semver1/system.text.json/6.0.6.json",
        "pkg:nuget/System.Text.Json": "https://api.nuget.org/v3/registration5-semver1/system.text.json/index.json",
        "pkg:nuget/Newtonsoft.Json@13.0.3": "https://api.nuget.org/v3/registration5-semver1/newtonsoft.json/13.0.3.json",
        "pkg:nuget/EntityFramework": "https://api.nuget.org/v3/registration5-semver1/entityframework/index.json",
        "pkg:nuget/Serilog@3.1.1": "https://api.nuget.org/v3/registration5-semver1/serilog/3.1.1.json",
        # hex — with and without version
        "pkg:hex/plug@1.11.1": "https://hex.pm/api/packages/plug/releases/1.11.1",
        "pkg:hex/plug": "https://hex.pm/api/packages/plug",
        "pkg:hex/phoenix@1.7.10": "https://hex.pm/api/packages/phoenix/releases/1.7.10",
        "pkg:hex/ecto@3.11.0": "https://hex.pm/api/packages/ecto/releases/3.11.0",
        "pkg:hex/jason": "https://hex.pm/api/packages/jason",
        # pub — version is ignored (always package-level API)
        "pkg:pub/http@0.13.3": "https://pub.dev/api/packages/http",
        "pkg:pub/http": "https://pub.dev/api/packages/http",
        "pkg:pub/flutter_bloc@8.1.3": "https://pub.dev/api/packages/flutter_bloc",
        "pkg:pub/provider": "https://pub.dev/api/packages/provider",
        # hackage — version joins with hyphen in .cabal URL
        "pkg:hackage/cli-extras@0.2.0.0": "https://hackage.haskell.org/package/cli-extras-0.2.0.0/cli-extras.cabal",
        "pkg:hackage/cli-extras": "https://hackage.haskell.org/package/cli-extras.json",
        "pkg:hackage/aeson@2.2.1.0": "https://hackage.haskell.org/package/aeson-2.2.1.0/aeson.cabal",
        "pkg:hackage/lens": "https://hackage.haskell.org/package/lens.json",
        "pkg:hackage/text@2.0.2": "https://hackage.haskell.org/package/text-2.0.2/text.cabal",
        # golang — uppercase escaping, version prefix, nested namespaces
        "pkg:golang/xorm.io/xorm@v0.8.2": "https://proxy.golang.org/xorm.io/xorm/@v/v0.8.2.info",
        "pkg:golang/xorm.io/xorm": "https://proxy.golang.org/xorm.io/xorm/@v/list",
        "pkg:golang/example.com/M.v3@v3.1.0": "https://proxy.golang.org/example.com/!m.v3/@v/v3.1.0.info",
        "pkg:golang/golang.org/x/oauth2@0.29.0": "https://proxy.golang.org/golang.org/x/oauth2/@v/v0.29.0.info",
        "pkg:golang/github.com/gin-gonic/gin@v1.9.1": "https://proxy.golang.org/github.com/gin-gonic/gin/@v/v1.9.1.info",
        "pkg:golang/github.com/stretchr/testify@v1.8.4": "https://proxy.golang.org/github.com/stretchr/testify/@v/v1.8.4.info",
        "pkg:golang/google.golang.org/grpc": "https://proxy.golang.org/google.golang.org/grpc/@v/list",
        # maven — custom repository_url, deeply nested namespace
        "pkg:maven/org.apache.commons/commons-io@1.3.2": "https://repo.maven.apache.org/maven2/org/apache/commons/commons-io/1.3.2/commons-io-1.3.2.pom",
        "pkg:maven/org.apache.commons/commons-io": "https://repo.maven.apache.org/maven2/org/apache/commons/commons-io/maven-metadata.xml",
        "pkg:maven/org.apache.commons/commons-io@1.3.2?repository_url=https://repo1.maven.org/maven2": "https://repo1.maven.org/maven2/org/apache/commons/commons-io/1.3.2/commons-io-1.3.2.pom",
        "pkg:maven/com.google.guava/guava@32.1.3-jre": "https://repo.maven.apache.org/maven2/com/google/guava/guava/32.1.3-jre/guava-32.1.3-jre.pom",
        "pkg:maven/io.netty/netty-all@4.1.100.Final": "https://repo.maven.apache.org/maven2/io/netty/netty-all/4.1.100.Final/netty-all-4.1.100.Final.pom",
        "pkg:maven/org.springframework/spring-core": "https://repo.maven.apache.org/maven2/org/springframework/spring-core/maven-metadata.xml",
        # composer — version is ignored (always package-level API)
        "pkg:composer/psr/log": "https://repo.packagist.org/p2/psr/log.json",
        "pkg:composer/psr/log@1.1.3": "https://repo.packagist.org/p2/psr/log.json",
        "pkg:composer/laravel/framework@10.38.0": "https://repo.packagist.org/p2/laravel/framework.json",
        "pkg:composer/symfony/console": "https://repo.packagist.org/p2/symfony/console.json",
        "pkg:composer/monolog/monolog@3.5.0": "https://repo.packagist.org/p2/monolog/monolog.json",
        # cocoapods — version is ignored (always pod-level API)
        "pkg:cocoapods/AFNetworking@4.0.1": "https://trunk.cocoapods.org/api/v1/pods/AFNetworking",
        "pkg:cocoapods/AFNetworking": "https://trunk.cocoapods.org/api/v1/pods/AFNetworking",
        "pkg:cocoapods/Alamofire@5.8.1": "https://trunk.cocoapods.org/api/v1/pods/Alamofire",
        "pkg:cocoapods/SwiftyJSON": "https://trunk.cocoapods.org/api/v1/pods/SwiftyJSON",
        # conda — channel qualifier, default channel
        "pkg:conda/absl-py@0.4.1?channel=main": "https://api.anaconda.org/package/main/absl-py",
        "pkg:conda/numpy": "https://api.anaconda.org/package/main/numpy",
        "pkg:conda/pandas@2.1.4?channel=conda-forge": "https://api.anaconda.org/package/conda-forge/pandas",
        "pkg:conda/scipy@1.11.4": "https://api.anaconda.org/package/main/scipy",
        "pkg:conda/matplotlib?channel=conda-forge": "https://api.anaconda.org/package/conda-forge/matplotlib",
        # github — with and without version (release tag)
        "pkg:github/tg1999/fetchcode": "https://api.github.com/repos/tg1999/fetchcode",
        "pkg:github/nexb/scancode-toolkit@3.1.1": "https://api.github.com/repos/nexb/scancode-toolkit/releases/tags/3.1.1",
        "pkg:github/pallets/flask@3.0.0": "https://api.github.com/repos/pallets/flask/releases/tags/3.0.0",
        "pkg:github/torvalds/linux": "https://api.github.com/repos/torvalds/linux",
        "pkg:github/microsoft/vscode@1.85.0": "https://api.github.com/repos/microsoft/vscode/releases/tags/1.85.0",
        # gitlab — URL-encoded namespace/name, with and without version
        "pkg:gitlab/tg1999/firebase": "https://gitlab.com/api/v4/projects/tg1999%2Ffirebase",
        "pkg:gitlab/hoppr/hoppr@v1.11.1-dev.2": "https://gitlab.com/api/v4/projects/hoppr%2Fhoppr/releases/v1.11.1-dev.2",
        "pkg:gitlab/gitlab-org/gitlab-runner@v16.6.1": "https://gitlab.com/api/v4/projects/gitlab-org%2Fgitlab-runner/releases/v16.6.1",
        "pkg:gitlab/inkscape/inkscape": "https://gitlab.com/api/v4/projects/inkscape%2Finkscape",
        # bitbucket — always repo-level API
        "pkg:bitbucket/birkenfeld/pygments-main": "https://api.bitbucket.org/2.0/repositories/birkenfeld/pygments-main",
        "pkg:bitbucket/atlassian/python-bitbucket": "https://api.bitbucket.org/2.0/repositories/atlassian/python-bitbucket",
        "pkg:bitbucket/robeden/trove": "https://api.bitbucket.org/2.0/repositories/robeden/trove",
        # cran — with and without version
        "pkg:cran/ggplot2@3.4.0": "https://crandb.r-pkg.org/ggplot2/3.4.0",
        "pkg:cran/ggplot2": "https://crandb.r-pkg.org/ggplot2",
        "pkg:cran/dplyr@1.1.4": "https://crandb.r-pkg.org/dplyr/1.1.4",
        "pkg:cran/tidyverse": "https://crandb.r-pkg.org/tidyverse",
        "pkg:cran/shiny@1.8.0": "https://crandb.r-pkg.org/shiny/1.8.0",
    }

    for purl, url in purls_url.items():
        assert url == get_metadata_url(purl), f"Failed for {purl}"


def test_get_metadata_url_with_invalid_purls():
    purls = [
        "pkg:github",
        "pkg:cargo",
        "pkg:gem",
        "pkg:bitbucket",
        "pkg:gitlab",
        None,
    ]

    for purl in purls:
        with pytest.raises(Exception) as e_info:
            get_metadata_url(purl)
            assert "Invalid PURL" == e_info


def test_get_metadata_url_returns_none_for_missing_required_fields():
    # Types requiring namespace+name return None with only namespace
    assert get_metadata_url("pkg:github/tg1999") is None
    assert get_metadata_url("pkg:bitbucket/birkenfeld") is None
    assert get_metadata_url("pkg:gitlab/tg1999") is None
    assert get_metadata_url("pkg:maven/org.apache.commons") is None
    assert get_metadata_url("pkg:composer/psr") is None


def test_get_metadata_url_returns_none_for_unsupported_type():
    assert get_metadata_url("pkg:unknown/foo@1.0") is None
    assert get_metadata_url("pkg:swift/github.com/Alamofire/Alamofire@5.4.3") is None
    assert get_metadata_url("pkg:deb/debian/curl@7.88.1-10") is None
    assert get_metadata_url("pkg:rpm/fedora/curl@7.88.1") is None
    assert get_metadata_url("pkg:generic/openssl@3.0.0") is None


def test_get_metadata():
    mock_response = MagicMock()
    mock_response.json.return_value = {"name": "requests", "version": "2.28.0"}
    mock_response.headers = {"content-type": "application/json"}
    mock_response.raise_for_status = MagicMock()

    with patch("httpx.get", return_value=mock_response) as mock_get:
        result = get_metadata("pkg:pypi/requests@2.28.0")

        assert result == {"name": "requests", "version": "2.28.0"}
        mock_get.assert_called_once_with(
            "https://pypi.org/pypi/requests/2.28.0/json",
            headers={
                "Accept": "application/json",
                "User-Agent": "purl2meta",
            },
            timeout=30,
            follow_redirects=True,
        )


def test_get_metadata_returns_text_for_non_json():
    mock_response = MagicMock()
    mock_response.text = "<project><modelVersion>4.0.0</modelVersion></project>"
    mock_response.headers = {"content-type": "application/xml"}
    mock_response.raise_for_status = MagicMock()

    with patch("httpx.get", return_value=mock_response):
        result = get_metadata("pkg:maven/org.apache.commons/commons-io@1.3.2")
        assert "<project>" in result


def test_get_metadata_returns_none_for_unknown_type():
    result = get_metadata("pkg:unknown/foo@1.0")
    assert result is None
