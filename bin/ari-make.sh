#!/bin/bash

### Script adapted from Galaxy Training Network script
### https://github.com/galaxyproject/training-material/

set -e

function cleanup(){
	kill $(pgrep -f $(npm bin)/http-server) || true
}

trap cleanup EXIT

slides=$1
echo "====== $slides ======"
dir="$(dirname "$slides")"
pdf="$dir/$(basename "$slides" .html).pdf"
mp4="videos/$dir/$(basename "$slides" .html).mp4"
built_slides="_site/$slides"

# Launch small server
$(npm bin)/http-server -p 9876 _site &

# Process the slides
echo $built_slides
$(npm bin)/decktape automatic -s 1920x1080 http://localhost:9876/DNAnalyzer/$slides _site/DNAnalyzer/$pdf; \

# Build the slides
echo ari.sh "_site/DNAnalyzer/$pdf" "$slides" "$mp4"
./bin/ari.sh "_site/DNAnalyzer/$pdf" "$slides" "$mp4"

cleanup
