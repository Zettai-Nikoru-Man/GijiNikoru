#!/usr/bin/env bash

mysqldump -u root -ppassword -h db --no-create-info --default-character-set=utf8mb4 nicoru > $1
