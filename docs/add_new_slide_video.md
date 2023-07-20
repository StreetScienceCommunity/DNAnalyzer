# How do I add new slide?
Put the new slide markdown file in the corresponding chapter folder for example like `game/level1/intro/`.

And name it as `slides.md`

# How do I view the added slide deck?

At the root folder `DNAnalyzer`,

Use terminal and run the local Python http server
```
python3 -m http.server 9876
```

And view the slide deck by accessing the url 

`http://0.0.0.0:9876/assets/reveal.js/index.html?slides=$slide_md_path`

Change the $slide_md_path to the path of the slides.md file you want to view, for example 

`http://0.0.0.0:9876/assets/reveal.js/index.html?slides=/game/level1/intro/slides.md`