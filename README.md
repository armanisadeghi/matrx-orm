# matrx-orm

## Updating to a new version

1. Make local updates, test them and confirm they are good.
    - Check current tags: git tag
    - Identify the next tag to be used
2. commit and Push all updates
    - git commit -m "Update columns.py schema builder - v1.0.2"
    - git push origin main
3. Tag the commit:
    - git tag v1.0.2
    - git push origin v1.0.2
4. Confirm tags are properly updates:
    - git tag
    - Example:
        v1.0.0
        v1.0.2
5. Make updates to apps that need the updated version:
    - AI Dream pyproject.toml Example: 
    - Before: matrx-orm = { git = "https://github.com/armanisadeghi/matrx-orm", rev = "v1.0.0" }
    - After: matrx-orm = { git = "https://github.com/armanisadeghi/matrx-orm", rev = "v1.0.2" }