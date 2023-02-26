
@ui:
    streamlit run {{justfile_directory()}}/algove/streamlit_ui.py

@lint:
    ruff {{justfile_directory()}}/algove
    ruff {{justfile_directory()}}/algove
    printf "\n-------------✅ ruff  ✅ -----------------------\n"
    black --check {{justfile_directory()}}/algove
    printf "\n-------------✅ black ✅ -----------------------\n"


@typecheck:
    mypy {{justfile_directory()}}/algove
    printf "\n-------------✅ mypy  ✅ -----------------------\n"

@check: lint typecheck
    

@fix:
    black {{justfile_directory()}}/algove
    black {{justfile_directory()}}/tests
    ruff {{justfile_directory()}}/algove --fix
    ruff {{justfile_directory()}}/tests --fix

@test:
    python -m pytest tests

@docs:
    mkdocs build
    printf "\n-------------✅ mkdocs ✅ -----------------------\n"

@go: fix lint typecheck test 
    echo "Done."

@ci: check test docs
    echo '   | _ \ __ _    ___    ___    ___   __| |   | |'
    echo '   |  _// _` |  (_-<   (_-<   / -_) / _` |   |_|'
    echo '  _|_|_ \__,_|  /__/_  /__/_  \___| \__,_|  _(_)_'
    echo ' | """ _|"""""_|"""""_|"""""_|"""""_|"""""_| """ |'
    echo '  -0-0-  -0-0-  -0-0-  -0-0-  -0-0-  -0-0-  -0-0-'