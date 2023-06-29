# How do I add new quiz questions?

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

## In order to add a new level:
`init_yaml_to_db.py` file is designed to traverse through a predefined `levels` array to identify all levels.

To add a new level, you need to follow these two steps:
1. Append the new level name at the end of the `levels` array.
2. Create a new folder with the name `level#`. Here, the `#` symbol is a placeholder that should be replaced by a numerical value. This value must follow an ascending order relative to the previously existing level folders.

## In order to add a new chapter:
1. Add the new chapter folder with the name "chapter", followed by the incremental chapter ID.
2. In this folder, create a new file `quiz.yaml`, which stores all the questions within the chapter. 
3. Create a new folder `images`, and put all the images needed for the chapter into it.

## In order to add new questions to a `quiz.yaml`:

we need to add each one under the variable `questions`.
There are 5 types of questions (choose_one, choose_many, grid, grid_checkbox. open), which can be added in 3 different templates types:

### For choose_one and choose_many type questions:
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

### For grid, grid_checkbox questions:
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

### For open questions:
```
- title: # title of the question
  type: open
  hint: # hint of the question
  explanation: # explanation of the question shown on the result page
  point: # points the user will get if it's answered
  transition_sentence: # The transition sentence that will be shown in front of the question if it is shown in the form of a paper 
```

# How do I update existing quiz questions?
This section provides instructions on how to update certain parts of your project that don't affect the result of the question. 

If your updates concern fields such as `title`, `hint`, `explanation`, `choice` text (provided it doesn't change the result), or `transition_sentence`

Just modify the YAML file: Make the necessary changes in the relevant YAML file.

By following these steps, you can update the aforementioned fields without impacting the outcome of the question.


# Note:

1. **Be sure to run init_yaml_to_db.py: After making your changes, execute the init_yaml_to_db.py script**.


2. **It is strongly advised not to delete questions or alter fields that directly impact the outcome of a question, such as those determining correctness or point allocation.** This caution is primarily due to the fact that there might be users who have already completed the questions, with their results stored in the database.
Changes to these fields may cause inconsistencies between the stored results and the updated questions, potentially leading to confusion or errors in data interpretation. Always consider the potential implications for existing user data before making significant changes to question outcomes.

