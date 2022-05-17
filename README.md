# DNAnalyzer: an online game for DNA data analysis

***Involve and empower citizens to contribute to science***

## Welcome!

Welcome! :tada: Willkommen! :balloon: Grüezi! :confetti_ball: Bienvenue! :balloon::balloon::balloon:

Thank you for visiting the DNAnalyzer project repository.

This document (the README file) is a hub to give you some information about the project. Jump straight to one of the sections below, or just scroll down to find out more.

* [What are we doing? (And why?)](#what-are-we-doing)
* [Who are we?](#who-are-we)
* [What do we need?](#what-do-we-need)
* [How can you get involved?](#get-involved)
* [Get in touch](#contact-us)

## What are we doing?

### The problem

Especially in the last years public media is using words like sequencing, DNA, RNA, mutations, and variants, without easy to understand scientific explanations. Theses key words do not necessarily help informing the audience and sometimes leads to even more confusion.
As scientists it is our duty to not only report but also explain our work in an easy to understand way.
Technologies like DNA sequencing are getting cheaper and therefore more accessible for various applications, e.g. in personalized medicine. This produces more data. Platforms like Galaxy (Afgan et al., Nucl Acids Res , 2018) and the Galaxy training material (Batut et al., Cell syst, 2018) help scientists analyzing their own (complex) data in a user friendly way. However, for each analysis there are several ways to perform it. Experience and knowledge helps to achieve good results, but sometimes one has to test several combinations of different algorithms and parameter settings. This can be exhausting and time consuming.

### The solution

We are implementing an encouraging and easy-to-understand online game on DNA data analysis, the DNAnalyzer. 

We have some interesting story, to make the game more exciting. You can see them [here](stories/README.md)

The game, implemented in Galaxy, will consist of several levels: 
1. Learning: about biological background (DNA and sequencing) and how to use the platform. 
2. Hands on: perform the first guided data analysis.
3. Expert: change and improve their pipeline for data analysis.

Gamer will in the first two levels collect points by answering questions or finding treasures by following hints. In the third level gamer and reseachter will interactively evaluate dataanalysis of otheres and thereby give and get points. We believe that the integration of society into the scientific both will profit. Citizens will get excited for science and they can help to analyze and improve scientific data. 

## Who are we?

We are the [Street Science Community](https://streetscience.community), a group of researchers and teachers in Freiburg trying to bring DNA, sequencing, metagenomics and in general the scientific process closer to citizens. Therefore, we already developed the BeerDEcoded project: a series of hands-on workshops for pupils and citizens with the general aim of scientific outreach. During these workshops, we guide participants through the scientific project of the extraction and identification of different yeasts contained in a beer sample. The citizens are performing the whole process from opening the beer bottle to the last klick while performing the data analysis.
We generated protocols that lead the citizens through the extraction of yeast DNA, the identification via sequencing, and the analyzation of the sequenced DNA via an easy and straightforward user interface. Our aim is to make science tangible and accessible for everyone.


## What do we need?

**You**! In whatever way you can help.

We are searching for motivated students in computer science, who will be given a hiwi contract.
We also want to work closely with the Galaxy community, to get implementation ideas and tips.
We would like to get hints and inspiration from teachers and storytellers to improve the appeal of our game for users.
And of course any direct feedback of a non-researcher's opinion of the usability and gaming factor.

## Get involved

If you think you can help in any of the areas listed above (and we bet you can) or in any of the many areas that we haven't yet thought of (and here we're *sure* you can) then please check out our [contributors' guidelines](CONTRIBUTING.md) and our [roadmap](issues/1).

Please note that it's very important to us that we maintain a positive and supportive environment for everyone who wants to participate. When you join us we ask that you follow our [code of conduct](CODE_OF_CONDUCT.md) in all interactions both on and offline.


## Contact us

If you want to report a problem or suggest an enhancement we'd love for you to [open an issue](issues) at this github repository because then we can get right on it.


## Thank you

Thank you very much for visiting our project repository. We hope you feel inspired and welcomed to test or even contribute to our online microbiome data analysis.


## How can I generate the website locally?

You need a `ruby` environment (version >= 2.4). Either you have it installed and
you know how to [Bundler](https://bundler.io/) and
[Jekyll](https://jekyllrb.com/) or you use
(mini-)[conda](https://conda.io/docs/index.html), a package management system
that can install all these tools for you. You can install it by following the
instructions on this page: https://conda.io/docs/user-guide/install/index.html

In the sequel, we assume you use miniconda.

1. Open a terminal
2. Clone this GitHub repository:

   ```
   git clone https://github.com/StreetScienceCommunity/DNAnalyzer
   ```

3. Navigate to the `DNAnalyzer` folder with `cd`
4. Set up the conda environment:

   ```
   make create-env
   ```

5. Install the project's dependencies:

   ```
   make install
   ```

6. Start the website:

   ```
   make serve
   ```

7. Open the website in your favorite browser at:
   [http://127.0.0.1:4000/](http://127.0.0.1:4000/)



## Generate videos

### Requirements

Ubuntu

```
$ sudo apt-get install sox
$ sudo apt-get install libsox-fmt-mp3
```

#### Steps

In different terminals:

1. Run website 
1. Launch MozillaTTS for speech

   ```
   $ docker run -it -p 5002:5002 synesthesiam/mozillatts
   ```

2. Launch scripts

   ```
   $ conda activate dnanalyzer
   $ ./bin/ari-make.sh <path to slide>
   ```
   
## How can I add a new level to the game?

1. Create a new directory game/levelX, where X is the number of new level. 

2. In game/levelX:

- Create slides.html using markdown pattern:

```
---
layout: slides
title: Level X - <title of level>

---
### Title
content of slide
![alternative text for image] (images/<name of image file>)

[Source/link to original image]

???

Text for the voice
Split by sentence
1 sentence starting with “-”

```

- Create a folder “images”, put all images used in slides.html for this level there

- Create index.md using pattern:

 For NOT last level:

```
---
layout: level
title: DNAnalyzer
description: 'Level X - <name of level>’
image: /images/index.png
quiz: <Embed HTML of google form used for this level quiz>
scores: <Embed HTML of google sheets used for this level scores>
---

[**Next level**]({{ site.baseurl }}{% link game/level<X+1>/index.md %}){:.button .is-link .is-large}
```

 For last level:

```
---
layout: level
title: DNAnalyzer
description: 'Level X - <name of level>’
image: /images/index.png
quiz: <Embed HTML of google form used for this level quiz>
scores: <Embed HTML of google sheets used for this level scores>
---

[**Results**](http://streetscience.community/DNAnalyzer/index#results){:.button .is-link .is-large}
```

- Generate video (see section “Generate videos”) from slides.html. Add video with name video.mp4

### How can I create a quiz for a new level?
Quiz is realized with google forms. Results are located in Google Sheets https://drive.google.com/drive/folders/19Hiaqqvoue3M2YpA-LePUFe81fmZdNbu 

1. Create google form with questions based on content of slides.html

- First required question is “Your Username (use the same Username at all levels)”

- Turn on the option “Limit to 1 response”

- Set up correct answers and points for every question

2. Link google form with google sheet 

- Create new page”lvlX”  in google sheet https://docs.google.com/spreadsheets/d/1lPF_mXTmSa4BJDRjnd6_pwXCia7NDxlDJ6VlRMM0K18/edit#gid=906511743

- Link gform with this page responses -> create google sheet -> select existing google sheet

3. In scores google sheet

- Create page “Level X” which will be cleaned up from unneeded information and shared in game

- Add 2 columns “Username” with formula =’lvlX’!A:A, “Score” with formula =’lvlX’!B:B

- In the page “Results” open hidden columns with levels, add level X with formula ==IFERROR(VLOOKUP(A:A,'Level X'!A:B,2,FALSE),"")

- In column “Max level” add new sum term +IF(ISNUMBER(X:X),1,0) in formula, where X is column for new added level

- In column “Final score” change the range of cells, make sure that cells with a new added level are taken into account.

#### Colour codes

#aabeff4b - footer and header colours
#b1c4ff1a - background colour
#E5f0f9 - colour used in gforms and gsheets
