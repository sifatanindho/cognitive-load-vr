# AI Agent to Adapt Lego Task Difficulty Based on Team Cognitive Load

## Overview
The project builds on cognitive load theory (CLT) and adaptive learning research. CLT emphasizes that human working memory is limited, so learning tasks should impose a moderate cognitive load​. Flow theory and the Zone of Proximal Development likewise suggest that tasks are most engaging when challenge matches the participants’ skill (not too easy or too hard)​. In recent HCI and educational research, dynamic difficulty adjustment (DDA) is used to keep cognitive load in an optimal range – systems automatically modify task parameters in real time based on user performance​. The novel aspect here is applying these ideas to a collaborative team task (Lego building). Team cognitive load research highlights that group tasks create a “collective cognitive burden”​; this project aims to measure that load (via time/errors) and adapt task difficulty to keep the team in a sweet spot of engagement and performance.

This is the codebase for that agent.

## Agent pipeline

Data module: After each task, compute time and error inputs.

Prediction module: Feed inputs to the trained model to get a load estimate.

Adjustment module: Output a new piece count for the next task based on load estimate.

Interface/Task module: Build a random Lego structure with the adjusted piece count and plot images of each side for the next task.

Data is collected from user studies through a light weight interface on tablets. A logistic regression model trained on a different labeled dataset is used to estimate load. With the load as an input variable, a piece count is computed using a rules-based approach. The agent then generates a configuration of a lego structure to build for the next task with the number of blocks, and the side images are sent to the user interface.

## Setup
```conda env create -f environment.yml```
```conda activate cog-vr```

## Training on a labeled dataset
```python src/model.py --dataset /path/to/custom_dataset.csv --model_type logistic_regression``` 

If you wanna use the default dataset and model leave args blank

## Evaluating model on a labeled dataset
```python src/evaluate.py``` 

This will evaluate the latest model you trained on the latest dataset you used. Running this without running ```model.py``` is pointless

## Running the user study interface

First, make sure lego_images/ directory is empty. Then run the following:

```python src/decision_maker.py```

```python user_study_app/app.py```

## User study guidelines

1. Share the URL with the ip address from the logs with all 4 participants
2. Fill out the index page with group id (should be the same), participant id (1, 2, 3, 4) and the experiment type on all the devices and click "Begin"
3. Read out loud:
   
"In this study, you will all be building 5 different lego structures together in 5 phases, or tasks. When you start each task, you will each see an image of one side of the structure and will be working collaboratively to rebuild a structure with a side that matches your image. The image will disappear after 2 minutes, so make sure to remember your structure well enough or finish quickly. After finishing each task, you will see your image again and will be asked to report the number of errors. An error is a block that was missed or incorrect. So, if a block is placed where it should be empty, or if it's missing when there should be one, or if you had the block placed where it should be but the color was wrong -- those are all considered as an error. Good luck!"
6. Ask them to start the task at the same time
7. Pictures show up, tell them to all click on finish only when the whole team is done
8. Ask them to fill out the report individually and then click on submit when everyone is done.
9. Repeat 3-5 until Task 5 ends
10. Check if reports.json has all the group info
