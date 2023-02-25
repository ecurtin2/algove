
@lint:
    ruff {{justfile_directory()}}/app
    ruff {{justfile_directory()}}/app
    printf "\n-------------✅ ruff  ✅ -----------------------\n"
    black --check {{justfile_directory()}}/app
    printf "\n-------------✅ black ✅ -----------------------\n"

@check: lint
    mypy {{justfile_directory()}}/app
    printf "\n-------------✅ mypy  ✅ -----------------------\n"

@fix:
    black {{justfile_directory()}}/app
    black {{justfile_directory()}}/tests
    ruff {{justfile_directory()}}/app --fix
    ruff {{justfile_directory()}}/tests --fix

@test:
    python -m pytest tests


ci_success_msg := ''' 
   | _ \ __ _    ___    ___    ___   __| |   | |   
   |  _// _` |  (_-<   (_-<   / -_) / _` |   |_|   
  _|_|_ \__,_|  /__/_  /__/_  \___| \__,_|  _(_)_  
_| ``` _|````| |````` |`````` |```` |````` |`````| 
 `-0-0- `-0-0- `-0-0- `-0-0- `-0-0- `-0-0- `-0-0-' 
'''

@docs:
    mkdocs build
    printf "\n-------------✅ mkdocs ✅ -----------------------\n"

@ci: check test docs
    echo '   | _ \ __ _    ___    ___    ___   __| |   | |'
    echo '   |  _// _` |  (_-<   (_-<   / -_) / _` |   |_|'
    echo '  _|_|_ \__,_|  /__/_  /__/_  \___| \__,_|  _(_)_'
    echo ' | """ _|"""""_|"""""_|"""""_|"""""_|"""""_| """ |'
    echo '  -0-0-  -0-0-  -0-0-  -0-0-  -0-0-  -0-0-  -0-0-'