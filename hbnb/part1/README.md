# HBnB Evolution - Technical Documentation (Part 1)

## Description / Presentation
HBnB Evolution is an AirBnB-inspired application that allows users to manage home listings, reviews, amenities, and user profiles, while emphasizing a clear, scalable, and well-documented software architecture.
This initial phase of the project is dedicated to creating comprehensive technical documentation, which will provide a clear foundation and reference for the upcoming development stages.

## UML and Diagram
0. High-Level Package Diagram
1. Detailed Class Diagram for Business Logic Layer
2. Sequence Diagrams for API Calls
3. Documentation Compilation


## Project Structure

##### 0. High-Level Package Diagram
This diagram illustrates the three-layer architecture of the HBnB application and the communication between these layers via the facade model. This diagram provides a conceptual overview of the organization of the various application components and their interactions.

##### 1. Detailed Class Diagram for Business Logic Layer
This diagram represents the entities of this layer, their attributes, methods, and relationships. The main objective is to provide a clear and detailed visual representation of the core business logic, focusing on the key entities: 
- User
- Location
- Review
- Equipment

The diagram details the attributes and methods, the relationships between classes (`1-to-N`, `N-to-N`), the timestamps (`created_at`, `updated_at`), and the unique identifiers (IDs).

##### 2. Sequence Diagrams for API Calls
Sequence diagrams help visualize how different system components interact to address specific use cases, illustrating the step-by-step process of handling API requests. There will be four of them flow : 
- User Registration
- Place Creation
- Review Submission
- Place Listing Retrieval

##### 3. Documentation Compilation
This document serves as a blueprint for the HBnB project, guiding the implementation phases and providing a reference for the system's architecture and design, compiling all diagrams and explanatory notes.

## Authors
Vivien Bernardot https://github.com/voicedhealer 
Anaïs choisy https://github.com/o0anais0o 
