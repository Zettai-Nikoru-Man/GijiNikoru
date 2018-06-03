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

# Downgrade db schema
alias dc-db-downgrade='dc exec api flask db downgrade'

# Log in to api server
alias dc-in-api='dc exec api bash'

# Log in to web server
alias dc-in-web='dc exec web bash'

# Show log
alias dc-log='dc logs -f --tail=200'

# Show aliases
alias dc-alias='alias dc; alias | grep "^alias dc\-"'

# Test nicoru get
alias dc-test-get-nicoru=test_get_nicoru

# Test nicoru put
alias dc-test-put-nicoru=test_put_nicoru

# Pip install
alias dc-pip-install='dc exec api pip install --upgrade pip && dc exec api pip install -r requirements.txt'

# Run pytest
alias dc-test=dc_func_run_pytest

# Run pytest
alias dc-test-all=dc_func_run_pytest_all

# Run pytest with collecting coverage
alias dc-test-cov=dc_func_run_pytest_with_coverage

# Run all pytest with collecting coverage
alias dc-test-all-cov=dc_func_run_pytest_all_with_coverage

# Run Python module
alias dc-py=dc_func_run_python_module

# Refresh chrome extension
alias dc-refresh-chrome-extension=dc_func_refresh_chrome_extension

# Apache bench test get nicoru
alias dc-ab-get-nicoru=dc_func_ab_get_nicoru

# Apache bench test put nicoru
alias dc-ab-put-nicoru=dc_func_ab_put_nicoru
