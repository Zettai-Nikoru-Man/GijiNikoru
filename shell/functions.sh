#!/usr/bin/env bash

function test_get_nicoru() {
    curl http://0.0.0.0/nicoru/$1
}

function test_put_nicoru() {
    curl -XPUT http://0.0.0.0/nicoru/$1 -H "Content-Type: application/json" -d "{\"cid\":\"$2\"}"
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
            test_put_nicoru $3 $4
            return
        fi
        return
    fi
    echo 'illegal input.'
}

function dc_func_run_pytest() {
    docker-compose exec api pytest $1 $2
}

function dc_func_run_pytest_all() {
    dc_func_run_pytest $1 /usr/test/app/
}

function dc_func_run_pytest_with_coverage() {
    docker-compose exec api pytest --cov=/usr/src/app -vv --cov-report html:/tmp/giji_nikoru/pytest_coverage $1
}

function dc_func_run_pytest_all_with_coverage() {
    docker-compose exec api pytest --cov=/usr/src/app -vv --cov-report html:/tmp/giji_nikoru/pytest_coverage /usr/test/app
}

function dc_func_run_python_module() {
    docker-compose exec api python $1
}

function dc_func_refresh_chrome_extension() {
    docker-compose exec front yarn install --pure-lockfile
    docker-compose exec front npm run lint
    docker-compose exec front npm run bundle
}

# usage: dc_func_ab_get_nicoru -c 100 -n 1000 -v 4
function dc_func_ab_get_nicoru() {
    docker-compose exec api ab "$@" web/nicoru/1
}

# usage: dc_func_ab_put_nicoru -c 100 -n 1000 -v 4
function dc_func_ab_put_nicoru() {
    docker-compose exec api ab -p /usr/test/app/data/data.json -m PUT -T application/json "$@" web/nicoru/1
}

function dc_func_db_export_impl() {
    docker-compose exec db mysqldump -u root -ppassword --tab=/tmp/dump/ --fields-terminated-by=, --fields-enclosed-by='"' --fields-escaped-by='\\' --default-character-set=utf8mb4 nicoru $1
    docker-compose exec db rm /tmp/dump/$1.sql
    docker-compose exec db mv /tmp/dump/$1.txt /tmp/dump/$1.csv
#    docker-compose exec db mv /tmp/dump/$1.csv /tmp/input/$1.csv
}

function dc_func_db_export() {
    dc_func_db_export_impl nicoru
    dc_func_db_export_impl video
    dc_func_db_export_impl comment
    dc_func_db_export_impl irregular_video_id
}

function dc_func_db_import() {
    docker-compose exec db mysqlimport --fields-terminated-by=, --fields-enclosed-by='"' --fields-escaped-by='\\' --default-character-set=utf8mb4 --local -u root -ppassword nicoru /tmp/input/nicoru.csv
    docker-compose exec db mysqlimport --fields-terminated-by=, --fields-enclosed-by='"' --fields-escaped-by='\\' --default-character-set=utf8mb4 --local -u root -ppassword nicoru /tmp/input/video.csv
    docker-compose exec db mysqlimport --fields-terminated-by=, --fields-enclosed-by='"' --fields-escaped-by='\\' --default-character-set=utf8mb4 --local -u root -ppassword nicoru /tmp/input/comment.csv
    docker-compose exec db mysqlimport --fields-terminated-by=, --fields-enclosed-by='"' --fields-escaped-by='\\' --default-character-set=utf8mb4 --local -u root -ppassword nicoru /tmp/input/irregular_video_id.csv
}
