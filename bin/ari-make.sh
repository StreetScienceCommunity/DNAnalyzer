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
slides_md="$dir/slides.md"

# Launch small server
$(which python3) -m http.server 9876 &

# Process the slides
# Pass the slide file name as a URL parameter
docker run --network host -v $(pwd):/slides astefanutti/decktape automatic -s 1920x1080 ttp://0.0.0.0:9876/assets/reveal.js/index.html?slides=$slides $pdf; \

# Build the slides
echo ari.sh "$pdf" "$slides_md" "$mp4"
./bin/ari.sh "$pdf" "$slides_md" "$mp4"

cleanup
