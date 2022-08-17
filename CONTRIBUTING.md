# How to contribute?

:+1::tada: First, thanks for taking the time to contribute! :tada::+1:

You can make this project better by contributing to it. You can report mistakes
and errors, create more content, etc. Whatever your background is, there is a
way to contribute: via the GitHub website, via command-line or even without
dealing with GitHub.

We will address your issues and/or assess your change proposal as promptly as we
can, and help you become a member of our community.

## How can I report mistakes or errors?

The easiest way to start contributing is to [file an issue](issues/new) to tell
us about a problem such as a typo, spelling mistake, or a factual error. You can
then introduce yourself and meet some of our community members.

## How can I get started with contributing?

This repository stores information and galaxy tours for our data science online game. Have a look. Maybe you already get some first ideas. Feel free to contact us if you want to contribute with or without new ideas. 

## How can I contribute in "advanced" mode?

For now our content is written in
[GitHub Flavored Markdown](https://guides.github.com/features/mastering-markdown/).

To manage changes, we use
[GitHub flow](https://guides.github.com/introduction/flow/) based on Pull
Requests:

1. [Create a fork](https://help.github.com/articles/fork-a-repo/) of this
   repository on GitHub
2. Clone your fork of this repository to create a local copy on your computer
3. Create a new branch in your local copy for each significant change
4. Commit the changes in that branch
5. Push that branch to your fork on GitHub
6. Submit a pull request from that branch to the master repository
7. If you receive feedback, make changes in your local clone and push them to
   your branch on GitHub: the pull request will update automatically
8. Pull requests will be merged by the street science community after at least one
   person has reviewed and approved the pull request.

## What can I do to help the project?

In issues, you will find lists of issues to fix and features to implement. Feel
free to work on them! You can check our [roadmap](../../issues/1) for upcoming tasks.
And feel free to contact us with new ideas at any time via the [an issue](issues/new) or E-mail.

## More specific questions and answers

### How do I add new questions?

There's a folder `game` in the project root. The folder structure is shown below:
```bash
├──   game
│   └──   level1
│       ├──   chapter1
│       │   ├──   quiz.yaml
│       │   ├──   images
│       │   │   ├──   bird_and_lizard.png
│       │   │   ├──   cell.png
│       │   │   ├──   ...
│       ├──   chapter2
│       │   ├──   quiz.yaml
│       │   ├──  images
│       │   │   ├──   dna-with-mutation.png
│       │   │   ├──   ...
│       ├──   chapter3
│       │   ├──   quiz.yaml
│       │   ├──   images
│       │   │   ├──   dna-sequencing_med.png
│       │   │   ├──   ...
│   └──   level2
│       ├──   chapter1
│       │   ├──   quiz.yaml
│       │   ├──   images
│       │   │   ├──   ...
```

In order to add a new chapter:
1. add the corresponding chapter folder with the name "chapter", followed by the incremental chapter ID.
2. In this folder, create a new file `quiz.yaml`, which stores all the questions within the chapter. 
3. Create a new folder `images`, and put all the images needed for the chapter into it.

For adding questions in `quiz.yaml`, we need to add each one under variable `questions`,
there are 4 types of questions (choose_one, choose_many, grid, grid_checkbox), and templates for each type of questions:
For choose_one and choose_many type questions:
```
- title: # title of the question
  type: choose_one / choose_many
  hint: # hint of the question
  explanation: # explanation of the question shown on the result page
  image_name: # name with extension of the image file (which is stored in the images folder in the current chapter)
  point: # points the user will get if it's answered correctly
  choices:
    - 1: # text of the choice
      correct: true / false
    - 2: # text of the choice
      correct: true / false
     ...
```

For grid, grid_checkbox questions:
```
- title: # title of the question
  type: grid / grid_checkbox
  hint: # hint of the question
  explanation: # explanation of the question shown on the result page
  image_name: # name with extension of the image file (which is stored in the images folder in the current chapter)
  point: # points the user will get if it's answered correctly
  choices:
    1: # text of the choice
    2: # text of the choice
    3: # text of the choice
    4: # text of the choice
  questions:
    - text: # text of the sub-question
      answers: [3] # list of choices which are correct, for grid questions, there should only be one element in the list
    - text: # text of the sub-question
      answers: [1,3] # list of choices which are correct, for grid questions, there should only be one element in the list
    - text: # text of the sub-question
      answers: [2] # list of choices which are correct, for grid questions, there should only be one element in the list
    - text: # text of the sub-question
      answers: [4, 2] # list of choices which are correct, for grid questions, there should only be one element in the list
    ...
```