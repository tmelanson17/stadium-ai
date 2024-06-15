#!/bin/bash

MOVELIST="config/moves/movelist"

while read -r LINE; do
    node query_movedex.js --move="${LINE}"
done < ${MOVELIST}
