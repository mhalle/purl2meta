# purl2meta

Resolve [Package URLs (purl)](https://github.com/package-url/purl-spec) to registry metadata API URLs.

Given a purl like `pkg:pypi/requests@2.28.0`, purl2meta returns the corresponding registry API endpoint — `https://pypi.org/pypi/requests/2.28.0/json` — so you can fetch package metadata without hardcoding registry-specific URL patterns.

## Installation

```bash
pip install purl2meta
```

To also fetch metadata over HTTP (installs [httpx](https://www.python-httpx.org/)):

```bash
pip install purl2meta[fetch]
```

## Quick start

### Get a metadata URL

```python
from purl2meta import get_metadata_url

get_metadata_url("pkg:pypi/requests@2.28.0")
# => "https://pypi.org/pypi/requests/2.28.0/json"

get_metadata_url("pkg:npm/express@4.18.2")
# => "https://registry.npmjs.org/express/4.18.2"

get_metadata_url("pkg:maven/org.apache.commons/commons-io@1.3.2")
# => "https://repo.maven.apache.org/maven2/org/apache/commons/commons-io/1.3.2/commons-io-1.3.2.pom"

get_metadata_url("pkg:cargo/serde@1.0.193")
# => "https://crates.io/api/v1/crates/serde/1.0.193"
```

Returns `None` for unsupported types or purls missing required fields.

### Fetch metadata directly

Requires the `[fetch]` extra.

```python
from purl2meta import get_metadata

data = get_metadata("pkg:pypi/requests@2.28.0")
# => {"info": {"name": "requests", "version": "2.28.0", ...}, "urls": [...], ...}

data = get_metadata("pkg:npm/express@4.18.2")
# => {"name": "express", "version": "4.18.2", "dependencies": {...}, ...}
```

`get_metadata` resolves the URL, sends an HTTP GET, and returns parsed JSON (or raw text for non-JSON responses like Maven POM files). Returns `None` if the purl type is unsupported.

## Supported package types

| Type | Example purl | Metadata API |
|------|-------------|-------------|
| npm | `pkg:npm/express@4.18.2` | registry.npmjs.org |
| PyPI | `pkg:pypi/requests@2.28.0` | pypi.org/pypi |
| Cargo | `pkg:cargo/serde@1.0.193` | crates.io/api |
| RubyGems | `pkg:gem/rails@7.1.2` | rubygems.org/api |
| NuGet | `pkg:nuget/Newtonsoft.Json@13.0.3` | api.nuget.org |
| Hex | `pkg:hex/phoenix@1.7.10` | hex.pm/api |
| Pub | `pkg:pub/http@0.13.3` | pub.dev/api |
| Hackage | `pkg:hackage/aeson@2.2.1.0` | hackage.haskell.org |
| Go | `pkg:golang/golang.org/x/oauth2@0.29.0` | proxy.golang.org |
| Maven | `pkg:maven/org.apache.commons/commons-io@1.3.2` | repo.maven.apache.org |
| Composer | `pkg:composer/laravel/framework@10.38.0` | repo.packagist.org |
| CocoaPods | `pkg:cocoapods/Alamofire@5.8.1` | trunk.cocoapods.org |
| Conda | `pkg:conda/numpy?channel=conda-forge` | api.anaconda.org |
| GitHub | `pkg:github/pallets/flask@3.0.0` | api.github.com |
| GitLab | `pkg:gitlab/inkscape/inkscape` | gitlab.com/api |
| Bitbucket | `pkg:bitbucket/birkenfeld/pygments-main` | api.bitbucket.org |
| CRAN | `pkg:cran/ggplot2@3.4.0` | crandb.r-pkg.org |

## API reference

### `get_metadata_url(purl: str) -> str | None`

Return the metadata API URL for the given purl string, or `None` if the type is unsupported or required fields are missing.

### `get_metadata(purl: str) -> dict | str | None`

Fetch metadata from the registry. Returns parsed JSON as a dict, raw text for non-JSON responses (e.g. Maven POM XML), or `None` if unsupported. Requires `httpx`.

### `metadata_router`

The underlying `Router` instance. Use it to register custom routes:

```python
from packageurl import PackageURL
from purl2meta import metadata_router

@metadata_router.route("pkg:custom/.*")
def build_custom_metadata_url(purl):
    purl_data = PackageURL.from_string(purl)
    return f"https://my-registry.example.com/api/{purl_data.name}"
```

## Development

```bash
git clone <repo-url>
cd purl2meta

# Run tests
uv run --with pytest --with httpx python -m pytest tests/ -v
```

## License

MIT
