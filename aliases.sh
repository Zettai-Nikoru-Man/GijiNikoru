#!/usr/bin/env bash
SCRIPT_PATH="$( cd "$(dirname "$BASH_SOURCE")"; pwd -P )"
export FLASK_APP=$SCRIPT_PATH/api/src/app/app.py
source $SCRIPT_PATH/shell/functions.sh

# alias for docker-compose
alias dc='docker-compose'

# Connect to DB
alias dc-db='dc exec db mysql --user=root --password=password nicoru'

# Generate migration script
alias dc-db-gen='dc exec api flask db migrate'

# Upgrade db schema
alias dc-db-upgrade='dc exec api flask db upgrade'

# Log in to api server
alias dc-in-api='dc exec api bash'

# Show log
alias dc-log='dc logs -f --tail=200'

# Show aliases
alias dc-alias='alias dc; alias | grep "^alias dc\-"'

# Test nicoru get
alias dc-test-get-nicoru=test_get_nicoru

# Test nicoru put
alias dc-test-put-nicoru=test_put_nicoru

# Pip install
alias dc-pip-install='dc exec api pip install -r requirements.txt'

# Run pytest
alias dc-test=run_pytest

# Run pytest
alias dc-test-all=run_pytest_all

# Run pytest with collecting coverage
alias dc-test-all-cov=run_pytest_all_with_coverage

# Run Python module
alias dc-py=dc_func_run_python_module
