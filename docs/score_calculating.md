# Workflow Scoring Scheme
This document describes the scoring scheme applied to a user's history and the given reference workflow, based on the tools used and the correctness of their parameters.

## Overview
The scoring scheme aims to encourage users to use correct tools, versions, and parameters in their workflows. The score for each workflow is calculated and then normalized to represent a percentage value.

The maximum possible score for each tool used in a workflow is 8 points, distributed as follows:

- 5 points for using the correct tool
- 1 point for using the correct version of the tool
- Up to 2 points for correctly using parameters of the tool

## Detailed Scoring Scheme
1. Initialize the total number of tools (num_of_tools) and the user's score (score) to 0.

2. Iterate over each tool result present in the 'comparison_by_reference_workflow_tools' section of the workflow result.

3. For each tool result, iterate over the detailed results.

4. For each step result in the details:
   - Increment num_of_tools by 1 for each tool encountered.
   - If the tool used in the step is the same as the reference tool, increment the score by 5 points.
   - If the version of the tool used is the same as the reference version, increment the score by 1 point.
   - If parameters are present and some parameters are incorrectly used, calculate the percentage of correct parameters. Subtract the number of wrong parameters from the total number of parameters in the workflow and divide the result by the total number of parameters in the workflow. If this percentage is positive, add to the score 2 times this percentage. If this percentage is negative, add nothing to the score.

5. After going through all tools, normalize the score by dividing the raw score by the product of the total number of tools and the maximum possible score per tool. Multiply the result by 100 to get a percentage and round it to two decimal places to get the normalized score.

## Conclusion
This scoring scheme rewards users for using the correct tools and parameters in their workflow, with a higher emphasis on tool selection. This encourages users to pay careful attention to tool selection, version control, and parameter usage in their workflows.


# Quiz questions score calculation method
## Type 'choose_one' and 'grid' questions
For each question in questions_dump of type 'choose_one' or 'grid':

- If the question ID is not in the form, mark it as 'missed'.

- For each choice in the question in the database:

  - If the choice is correct and the choice ID is in the submitted_answers, mark the choice as 'correct' and increment the selected_correct counter.

  - If the choice is correct but the choice ID is not in submitted_answers, mark the choice as 'missed'.

  - If the choice is not correct and the choice ID is in submitted_answers, mark the choice as 'wrong'.

  - If the choice is not correct and the choice ID is not in submitted_answers, increment the missed_wrong counter.

- If selected_correct is greater than 0, set the question score to the question's point value and add the question's point value to the cur_score.

- If selected_correct is 0, set the question score to 0.

## Type 'choose_many' and 'grid_checkbox' questions

- Set total_choice_num to 0.

- For each question with the same title:

- If the question ID is not in the form, mark it as 'missed'.

- For each choice in the question, increment total_choice_num.

  - If the choice is correct and the choice ID is in submitted_answers, mark the choice as 'correct' and increment selected_correct.

  - If the choice is correct but the choice ID is not in submitted_answers, mark the choice as 'missed'.

  - If the choice is not correct and the choice ID is in submitted_answers, mark the choice as 'wrong'.

  - If the choice is not correct and the choice ID is not in submitted_answers, increment missed_wrong.

- Calculate correct_sum as the sum of selected_correct and missed_wrong.

- If correct_sum is 0, set question_score to 0. Otherwise, set question_score as the rounded value of correct_sum divided by total_choice_num, multiplied by the question's point value.

- Add question_score to cur_score and set the question's score to question_score.

## Type 'open' questions

For each question:
- Check if the answer is empty or not
- if it's empty, give score 0
- else give the whole points