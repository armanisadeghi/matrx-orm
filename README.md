# matrx-orm

ORM utilities for the Matrx platform.

## Installation

### From PyPI (recommended)

```bash
pip install matrx-orm
# or with uv
uv add matrx-orm
```

### From GitHub (for development)

```bash
pip install git+https://github.com/armanisadeghi/matrx-orm.git
```

## Publishing a New Version

### Automated PyPI Publishing (Current Process)

The package automatically publishes to PyPI when you push a version tag. Here's the workflow:

1. **Make and test your changes locally**
   ```bash
   # Test your changes
   ```

2. **Update the version in pyproject.toml**
   ```toml
   version = "1.0.5"  # Increment appropriately
   ```

3. **Commit and push changes**
   ```bash
   git add .
   git commit -m "Add new feature - v1.0.5"
   git push origin main
   ```

4. **Create and push the version tag**
   ```bash
   git tag v1.0.5
   git push origin v1.0.5
   ```

5. **GitHub Actions automatically:**
   - Verifies the tag matches pyproject.toml version
   - Builds the package
   - Publishes to PyPI

6. **Update dependent projects**
   
   In projects like AI Dream, simply update the version:
   ```bash
   uv add matrx-orm@1.0.5
   # or manually in pyproject.toml:
   # matrx-orm = "^1.0.5"
   ```

### Version History

Check current tags: `git tag`

Example output:
```
v1.0.0
v1.0.2
v1.0.3
v1.0.4
```

### Important Notes

- **Always update pyproject.toml version before tagging**
- The GitHub Action will fail if tag version ≠ pyproject.toml version
- Semantic versioning: MAJOR.MINOR.PATCH (e.g., v1.0.5)
- Tags trigger automatic PyPI publishing
