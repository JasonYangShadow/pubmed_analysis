#!/bin/bash

mongod --dbpath data/db --logpath data/log 2>&1 &
