# AI Agent to Adapt Lego Task Difficulty Based on Team Cognitive Load

## Overview
This project builds on cognitive load theory (CLT) and adaptive learning research. CLT emphasizes that human working memory is limited, so learning tasks should impose a moderate cognitive load​. Flow theory and the Zone of Proximal Development likewise suggest that tasks are most engaging when challenge matches the participants’ skill (not too easy or too hard)​. In recent HCI and educational research, dynamic difficulty adjustment (DDA) is used to keep cognitive load in an optimal range – systems automatically modify task parameters in real time based on user performance​. The novel aspect here is applying these ideas to a collaborative team task (Lego building). Team cognitive load research highlights that group tasks create a “collective cognitive burden”​; this project aims to measure that load (via time/errors) and adapt task difficulty to keep the team in a sweet spot of engagement and performance.

This is the codebase for that agent.

## Agent pipeline

Data module: After each task, compute time and error inputs.
Prediction module: Feed inputs to the trained model to get a load estimate.
Adjustment module: Compare the estimate to the target. Output a new piece count for the next task based on your rules.
Interface/Task module: Build a random Lego structure with the adjusted piece count and plot images of each side for the next task.

Data is collected from user studies through a light weight interface on tablets. A logistic regression model trained on a different dataset from a VR cooking experiment is used to estimate load. With the load as an input variable, a piece count is computed using a rules-based approach. The agent then generates a configuration of a lego structure to build for the next task with the number of blocks, and the side images are sent to the user interface.
