# Researcher Overview

The `Researcher` is a software agent that has a particular perspective on the contents of the library which allows it to answer more specific queries. As new data arrives at the Library, it will understand each new data point, and use that data to answer user questions with greater nuance.

# Examples

## (Personal) Pottery Coach

A user has a collection of pottery images and notes about their pottery practice. The `Researcher` can help the user identify patterns in their work, suggest new techniques, and organize their catalog of pottery pieces.

## Health Coach

A user has a collection of health data, including diet logs, exercise routines, and sleep patterns. The `Researcher` can help the user identify correlations between different aspects of their health, suggest improvements, and track progress over time.

## Finance Advisor

A user has a collection of financial data, including income, expenses, investments, and savings goals. The `Researcher` can help the user create a budget, track spending, optimize investments, and plan for the future.

## Learning Assistant

A user has a collection of learning materials, including textbooks, articles, videos, and notes. The `Researcher` can help the user organize their study materials, create study plans, track progress, and recommend additional resources.

## Project Manager

A user has a collection of project data, including tasks, deadlines, resources, and milestones. The `Researcher` can help the user prioritize tasks, allocate resources, track progress, and adjust plans as needed.

# Implementation

Each implementation of the `Researcher` will be tailored to the specific domain and data types it is designed to work with.

Assume that the following "algorithms" are analogs to the prompts engineered to provide context to LLMs alongside a user query.

## Example Algorithm For Pottery Coach (Image only for now)

1. **Workflow Activation**: When a new image is added to the library, the `Researcher` is activated.
2. **Image Qualification**: The `Researcher` determines if the new image is a pottery piece or related to the user's pottery practice. Relevant is defined by the user.
3. **Image Analysis**: The `Researcher` analyzes the image to identify patterns, colors, shapes, and other visual features.
4. **Pattern Recognition**: The `Researcher` compares the new image to existing images in the library to identify similarities and differences.
5. **Technique Suggestions**: Based on the analysis and comparison, the `Researcher` suggests new techniques or improvements to the user.
5. **Catalog Organization**: The `Researcher` updates the user's pottery catalog with the new image and related information.

## Example Pottery Coach Algorithm that also leverages Knowledge Base

1. **Workflow Activation**: When a new image is added to the library, the `Researcher` is activated.
2. **Consult Knowledge Base**: The `Researcher` consults the knowledge base to gather core context about the `User` as a whole, and specifically about their pottery practice.
... (and so on)

## Example Pottery Coach Algorithm that can also ingest text notes

1. **Workflow Activation**: When a new image or text note is added to the library, the `Researcher` is activated. A special `Text Workflow` is triggered.
2. **Text Qualification**: The `Researcher` determines if the new text note is related to the user's pottery practice.
3. **Text Analysis**: The `Researcher` analyzes the text to identify keywords, topics, and other textual features.