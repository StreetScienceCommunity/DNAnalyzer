## Generate videos

### Requirements

Ubuntu

```
$ sudo apt-get install sox
$ sudo apt-get install libsox-fmt-mp3
```

### Steps

In different terminals:

1. Launch MozillaTTS for speech

   ```
   $ docker run -it -p 5002:5002 synesthesiam/mozillatts
   ```

2. Launch scripts

   ```
   $ conda activate dnanalyzer
   $ ./bin/ari-make.sh <path to slide>
   ```

You need to modify `<path to slide>`, e.g `./bin/ari-make.sh game/level1/intro/slides.md`
