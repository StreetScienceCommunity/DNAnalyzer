#!/bin/bash

### Script adapted from Galaxy Training Network script
### https://github.com/galaxyproject/training-material/

set -e

function cleanup(){
	kill $(lsof -t -i:9876)
}

trap cleanup EXIT

slides=$1
echo "====== $slides ======"
dir="$(dirname "$slides")"
pdf="videos/$dir/$(basename "$slides" .html).pdf"
mp4="videos/$dir/$(basename "$slides" .html).mp4"
yaml_md="$dir/slides_yaml.md"

# Launch small server
$(which python3) -m http.server 9876 &

# Process the slides
docker run --network host -v $(pwd):/slides astefanutti/decktape automatic -s 1920x1080 http://localhost:9876/$slides $pdf; \

# Build the slides
echo ari.sh "$pdf" "$yaml_md" "$mp4"
./bin/ari.sh "$pdf" "$yaml_md" "$mp4"

cleanup
