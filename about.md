---
layout: default
title: About DNAnalyzer
image: /images/about.jpg
photos:
  name: Soumil Kumar
  url: https://www.pexels.com/photo/photo-of-person-typing-on-computer-keyboard-735911/
---

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

<div class="people">
  {% for entry in site.data['people'] %}
    {% assign username = entry[0] %}
    {% include _includes/people.html username=username %}
  {% endfor %}
</div>

## Our values

We have high ethical standards, including:

- **Education**: Help educate the public about science and biotechnology, their
  benefits and implications
- **Transparency**: Emphasize transparency and the sharing of ideas, knowledge, data,
  protocols and results.
- **Open science**: Promote citizen science and decentralized access to science.
- **Modesty** Know you don't know everything.
- **Community**: Carefully listen to any concerns and questions and respond honestly
- **Respect**: Respect humans and all living systems.
- **Responsibility**: Recognize the complexity and dynamics of living systems and our
  responsibility towards them.

## What do we need?

**You!** In whatever way you can help.

## Get involved

If you think you can help in any of the areas listed above (and we bet you can)
or in any of the many areas that we haven't yet thought of (and here we're sure
you can) then please check out [our contributors'
guidelines]({{ site.github.repository_url }}/blob/master/CONTRIBUTING.md) and
our [roadmap]({{ site.github.repository_url }}/blob/master/roadmap.md).

Please note that it's very important to us that we maintain a positive and
supportive environment for everyone who wants to participate. When you join us
we ask that you follow our [code of conduct]({{ site.github.repository_url
}}/blob/master/CODE_OF_CONDUCT.md) in all interactions both on and offline.


## Current Sponsors

Funding
- [University of Freiburg](https://uni-freiburg.de/)
- [de.NBI](https://www.denbi.de/), the German Network for Bioinformatics Infrastructure, for the MinION
