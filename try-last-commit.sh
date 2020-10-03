COMMIT=$(git rev-parse HEAD)
txt="
repos:
-   repo: https://github.com/jvrana/poetry-hooks
    rev: $COMMIT
    hooks:
    -   id: poetry-version-up
    -   id: poetry-export
    -   id: poetry-export
        name: poetry-export-dev
        args: ['--requirements', 'requirements-dev.txt', '--poetry', '--dev', '-vvv']
"
echo $txt > .last-commit.yaml