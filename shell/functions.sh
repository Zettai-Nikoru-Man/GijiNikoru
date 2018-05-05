#!/usr/bin/env bash

function test_get_nicoru() {
    curl http://0.0.0.0/nicoru/$1
}

function test_put_nicoru() {
    curl -XPUT http://0.0.0.0/nicoru/$1 -H "Content-Type: application/json" -d "{\"cid\":\"$2\", \"ca\":\"$3\", \"cp\":\"$4\"}"
}

function test_gn() {
    if [[ $1 == 'get' ]]; then
        echo 'get'
        if [[ $2 == 'ni' ]]; then
            echo 'nicoru'
            test_get_nicoru $3
            return
        fi
        return
    elif [[ $1 == 'put' ]]; then
        echo 'put'
        if [[ $2 == 'ni' ]]; then
            echo 'nicoru'
            test_put_nicoru $3 $4 $5 $6
            return
        fi
        return
    fi
    echo 'illegal input.'
}

function run_pytest() {
    docker-compose exec api pytest $1 $2
}

function run_pytest_all() {
    run_pytest $1 /usr/test/app/
}

function run_pytest_all_with_coverage() {
    docker-compose exec api pytest --cov=/usr/src/app -s -vv --cov-report html /usr/test/app
}

function dc_func_run_python_module() {
    docker-compose exec api python $1
}

function dc_func_refresh_chrome_extension() {
    docker-compose exec front yarn install --pure-lockfile
    docker-compose exec front npm run lint
    docker-compose exec front npm run bundle
}
