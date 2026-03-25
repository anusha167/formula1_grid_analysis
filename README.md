<div align="center">
  <img width="100" height="100" alt="logo_f1" src="https://github.com/user-attachments/assets/f3bad344-c789-42b8-96e9-223cede2998e" />


# F1 Grid Position Analytics
</div>

This is an interactive data analytics dashboard exploring the relationship between starting grid position and finishing position in Formula 1 (1950-2024).

## Table of Contents
- [Motivating Question](#motivating-question)
- [Why I built this](#why-i-built-this)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Dataset](#dataset)


## Motivating Question
Which F1 drivers consistently outperform their starting grid position?

## Why I built this
Last quarter, I took a class where we explored correlational analysis using Python basics. I wanted to take that foundation and build something real with it.

I'm wasn't an F1 fan to begin with. But I figured the best way to learn about something new is to dig into the data yourself. What better way to understand a sport than to let the numbers tell the story?

So I took a dataset spanning 75 years of Formula 1 racing and turned it into something I could actually interact with. Along the way, I became genuinely curious about the patterns I was finding.

## Features
- **General Correlation Analysis:** Pearson correlation between grid and finishing position
- **Individual Driver Analysis:** Select any driver, filter by year range, scatterplot, and season-by-season trend
- **Driver Comparative Analysis:** Pick 2 drivers and compare key metrics side by side

## Tech Stack
- Python
- Pandas
- Numpy
- Plotly
- Plotly Dash
- SciPy
- Gunicorn

## Dataset
Ergast F1 World Championship Dataset via Kaggle

Link: https://www.kaggle.com/datasets/rohanrao/formula-1-world-championship-1950-2020
