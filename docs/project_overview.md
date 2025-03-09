# Project Overview

This project is called `memory-machine`. `memory-machine` (MM) is a personalized, evolving `Library` that receives and catalogues a `User`'s input of any structure. MM enables `User`s to answer complex questions about their own history leverage automated, agentic `Researcher` , considering both the contents of the `Library` and the configuration context about the `User`. As more user data is added to the system, the library learns.

To recap, there are three major actors in our system:
- The Library, which houses the data
- The User, which provides new data
- The Researcher, which answers user questions about the data, and manage ingestion and cataloguing of new data. They play an active role in managing the state of the Library.

# Implementation Overview
Core logic is in Python.

The `Library` is a document database. It will provide direct access to raw and encoded representations of documents.
Current Implementation: TBD

The `Researcher` is a software agent that has a particular perspective on the contents of the library which allows it to answer more specific queries. As new data arrives at the Library, it will understand each new data point, and use that data to answer user questions with greater nuance.

Assumption: Large language/multimodal models will drive an agentic-first approach to knowledge base management.

To answer more complex questions from the user, a hierarchy of `Researcher` agents will actively iteratively develop a knowledge base. Each `Researcher` will maintain its own perspective of the data, while consulting the diversity and history of knowledge gathered by other agents.