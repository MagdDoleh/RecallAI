# RecallAI Development Instructions

## 1. Project Purpose

RecallAI is an AI-powered study platform.

A user enters a topic they want to learn about, such as:

- Database normalization
- Binary search trees
- Machine learning regression
- Operating system scheduling

RecallAI uses an AI API to dynamically generate study material for that topic.

Generated material may include:

- A topic summary
- Key concepts
- Flashcards
- Quiz questions

Users can save generated material to their personal account and return to it later.

RecallAI is both a portfolio project and a learning project.

The application should demonstrate good software engineering practices without becoming unnecessarily complicated.

The developer is learning full-stack development while building this project. Codex may perform significant implementation work, but the code must remain understandable enough that the developer can confidently explain how the application works.

Do not overengineer the project.

---

# 2. Core MVP

Version 1 should allow a user to:

1. Register an account.
2. Log in.
3. Log out.
4. Enter a study topic.
5. Generate study material using an AI API.
6. Display generated material in the browser.
7. Generate a summary and key concepts.
8. Generate flashcards.
9. Generate quiz questions.
10. Save generated study material.
11. View previously saved study material.
12. Open an individual saved topic.
13. Edit saved material.
14. Delete saved material.
15. Search saved material.
16. View basic account information.

Do not add major features outside this MVP unless explicitly requested.

Finish the core application before expanding its scope.

---

# 3. Technology Stack

## Frontend

Use:

- HTML
- CSS
- Vanilla JavaScript

Do not introduce React, Vue, Angular, or another frontend framework unless explicitly requested.

One purpose of this project is to understand how browser JavaScript directly communicates with a backend API.

---

## Backend

Use:

- Python
- FastAPI

FastAPI will expose the REST API used by the frontend.

---

## Database

Start with:

- SQLite

Use a relational database design.

PostgreSQL may be introduced later for deployment or additional learning.

Do not migrate to PostgreSQL before there is a reason to do so.

---

## AI

Use:

- Google Gemini API

Only one AI provider should be used for the MVP.

The Gemini-specific integration should be separated from unrelated application logic so another provider could reasonably replace Gemini later without rewriting the entire application.

Do not integrate multiple AI providers during the MVP.

---

## Authentication

Use:

- Secure password hashing
- JWT-based authentication

Never store plaintext passwords.

---

## Version Control

Use:

- Git
- GitHub

Use meaningful commits throughout development.

---

## Deployment

Initial deployment target:

- Render

AWS may be explored later as a separate learning step.

Do not introduce AWS into the initial MVP unless explicitly requested.

---

## CI/CD

GitHub Actions may be introduced after the core application works.

CI/CD should not delay development of the MVP.

---

# 4. Architecture

Keep the architecture organized but understandable.

The general application flow is:

Browser
    |
    v
JavaScript
    |
    | HTTP / JSON
    v
FastAPI Routes
    |
    v
Services / Application Logic
    |
    +----> Database
    |
    +----> Gemini Integration

Each part should have a clear responsibility.

---

## Routes

FastAPI routes handle HTTP concerns.

Routes may:

- Receive requests
- Validate request data
- Call the appropriate service
- Return responses
- Return appropriate HTTP status codes

Routes should not contain large amounts of unrelated application logic.

---

## Services

Services contain related application behavior.

Possible examples include:

- Authentication logic
- Study-generation logic
- Saved-note logic

A service file may contain multiple related functions.

DO NOT create a separate file for every function.

Split code into another file when there is a meaningfully different responsibility or when an existing file becomes difficult to understand.

---

## AI Integration

Code that directly communicates with Gemini should be isolated from unrelated application logic.

Gemini-specific concerns may include:

- API configuration
- Sending prompts
- Receiving responses
- Handling Gemini errors
- Parsing AI responses

A change to the Gemini integration should not require editing unrelated authentication, database, or HTTP code.

---

## Database / Data Access

Database operations should be separated from HTTP routing where practical.

Do not scatter database queries throughout unrelated files.

Keep the implementation straightforward during the MVP.

---

## Models

Models represent important application data.

Likely models include:

- User
- Topic
- Flashcard
- QuizQuestion

Do not create unnecessary models simply to increase architectural complexity.

---

# 5. Frontend Architecture

The frontend should be built in three conceptual layers:

HTML
    |
    | Structure
    v
JavaScript
    |
    | Behavior
    v
CSS
      Appearance

HTML defines what exists.

JavaScript defines what interactive elements do and communicates with the backend.

CSS controls presentation.

Keep these responsibilities reasonably separated.

---

# 6. Stable Frontend Contracts

The initial frontend should NOT be treated as disposable.

Build a simple but intentional HTML structure early in development.

Important interactive elements should use stable identifiers or other deliberate JavaScript hooks.

Examples may include:

- Topic input
- Generate button
- Study-results container
- Save button
- Login form
- Registration form
- Saved-note controls

JavaScript behavior should attach to these stable elements.

Later visual improvements should primarily modify:

- CSS
- Layout
- Typography
- Spacing
- Visual components
- Responsive behavior
- Loading states
- Empty states
- Error presentation

Do not casually rename, remove, or replace elements that existing JavaScript depends on.

If the HTML structure must change, update affected JavaScript deliberately and retest the feature.

---

# 7. Stable Backend Contracts

The frontend and backend communicate through API contracts.

Once an endpoint is being used by the frontend, do not casually rename it or change its expected request/response structure.

For example:

Frontend
    |
    | POST /generate
    v
FastAPI
    |
    v
Study generation
    |
    v
JSON response

Visual frontend changes should not require backend API changes unless there is a functional reason.

If an API contract needs to change, identify which frontend behavior depends on it and update both sides deliberately.

---

# 8. Initial Project Structure

Do NOT generate the entire final folder structure immediately.

Create files and folders as they become necessary.

The project may eventually resemble:

RecallAI/
|
|-- AGENTS.md
|-- LEARNING.md
|
|-- backend/
|   |
|   |-- main.py
|   |
|   |-- routes/
|   |
|   |-- services/
|   |
|   |-- models/
|   |
|   `-- database/
|
`-- frontend/
    |
    |-- login.html
    |-- register.html
    |-- dashboard.html
    |-- saved.html
    |-- account.html
    |
    |-- css/
    |
    `-- js/

This is a direction, not a requirement to create every directory immediately.

Use the smallest reasonable structure for the current development stage.

The developer should understand why a new file or folder is being introduced.

---

# 9. Planned REST API

The exact API may evolve.

Expected operations include endpoints similar to:

POST /register
Create a user.

POST /login
Authenticate a user.

POST /generate
Generate study material.

POST /topics
Save generated material.

GET /topics
Retrieve the authenticated user's saved topics.

GET /topics/{id}
Retrieve one saved topic.

PUT /topics/{id}
Update a saved topic.

DELETE /topics/{id}
Delete a saved topic.

The API should follow normal REST conventions where practical.

Do not force an endpoint design merely because it appears in this document if implementation reveals a better simple design.

Explain meaningful API-design changes before making them.

---

# 10. Planned Database Design

The initial relational model will likely include the following.

## Users

Possible fields:

- id
- username
- email
- password_hash
- created_at

---

## Topics

Possible fields:

- id
- user_id
- title
- summary
- created_at
- updated_at

A user can own multiple topics.

---

## Flashcards

Possible fields:

- id
- topic_id
- question
- answer

A topic can contain multiple flashcards.

---

## Quiz Questions

Possible fields:

- id
- topic_id
- question
- answer
- difficulty

A topic can contain multiple quiz questions.

---

This schema may evolve during implementation.

Do not add unnecessary tables merely to make the database appear more complicated.

---

# 11. Security Requirements

Security is an important learning goal.

Follow these rules:

- Never store plaintext passwords.
- Never hardcode API keys into source code.
- Never commit secrets to Git.
- Use environment variables for secrets.
- Validate important user input.
- Users must not be able to access another user's private saved material.
- Protected endpoints must verify authentication.
- Perform database operations safely.
- Explain security-sensitive implementation decisions.
- Do not expose the Gemini API key to frontend JavaScript.

External API calls requiring secret credentials should be made from the backend.

If a requested implementation creates an obvious security problem, explain the problem and use a safer straightforward implementation.

---

# 12. Primary Learning Goals

By the end of RecallAI, the developer should understand the following concepts through actual use in the project.

## Backend Development

- Python backend development
- FastAPI
- Routes
- Request handling
- Response handling
- Services
- Basic software architecture
- Client/server architecture

---

## Web and API Concepts

- What an API is
- REST APIs
- HTTP
- Requests and responses
- GET
- POST
- PUT
- DELETE
- HTTP status codes
- JSON
- Frontend/backend communication
- localhost
- Ports

---

## Databases

- SQL
- SQLite
- PostgreSQL basics
- Relational databases
- Tables
- Rows
- Primary keys
- Foreign keys
- Relationships
- CRUD
- Persistence

---

## Authentication and Security

- Authentication
- Authorization
- Password hashing
- JWT
- Protected endpoints
- Environment variables
- API key security

---

## External APIs

- Calling an external API
- API keys
- Sending requests
- Receiving responses
- Parsing JSON
- Handling API errors
- Gemini API integration

---

## Frontend

- HTML
- CSS
- JavaScript
- DOM manipulation
- Forms
- Event listeners
- fetch()
- Sending HTTP requests
- Displaying backend responses
- Loading states
- Error states

---

## Development Workflow

- Git
- GitHub
- Commits
- Debugging
- Reading error messages
- Testing endpoints
- Project organization
- Refactoring
- Regression testing

---

## Deployment

Later in development:

- Deployment
- Cloud hosting concepts
- Development vs production environments
- Production environment variables
- PostgreSQL in production
- GitHub Actions
- CI/CD

Possible later learning:

- AWS
- Docker

These later topics should not complicate the initial MVP.

---

# 13. Teaching and Implementation Rules

This section is extremely important.

The developer is learning how a full-stack application is constructed and is not expected to independently write the entire application from scratch.

Codex may perform substantial implementation work.

However, completing features quickly is NOT the only goal.

The developer must be able to understand and explain the resulting system.

When implementing code:

1. Prefer clear code over clever code.
2. Avoid unnecessary abstractions.
3. Avoid unexplained design patterns.
4. Keep functions reasonably focused.
5. Use descriptive names.
6. Do not over-comment obvious code.
7. Add comments when they explain something genuinely useful.
8. Avoid unnecessary dependencies.
9. Do not redesign unrelated parts of the application while implementing a small feature.
10. Build incrementally.
11. Prefer implementations a learning developer can trace from beginning to end.
12. Do not hide important behavior behind unnecessary abstraction.
13. Explain meaningful architectural decisions.
14. Do not introduce a new technology merely because it would make the project appear more advanced.

The goal is NOT to minimize how much code Codex writes.

The goal is for the developer to understand:

- What the code does
- Why it exists
- Where it belongs
- How data moves through the system
- How different parts communicate
- What can fail
- How to debug it

Do not require memorization of syntax.

Understanding behavior and architecture is more important than remembering exact syntax.

---

# 14. Development Process

Build RecallAI one phase at a time.

Do NOT build the entire application from this document in one operation.

Do NOT proceed into the next phase unless explicitly requested.

---

## Phase 1: Project and FastAPI Setup

Build only what is needed to establish a working backend.

Tasks may include:

- Create the minimal backend structure.
- Create a Python virtual environment.
- Install FastAPI and the required local server.
- Create main.py.
- Run FastAPI locally.
- Create one simple test endpoint.
- Access the endpoint locally.
- Inspect the returned response.

Learning focus:

- Python environments
- Dependencies
- FastAPI
- Backend servers
- localhost
- Ports
- Routes
- HTTP
- JSON

---

## Phase 2: Frontend Structure and First Connection

Create the basic frontend structure.

Do not attempt final visual polish.

Tasks may include:

- Establish the general application layout.
- Create semantic HTML for the first interface.
- Add minimal CSS for usability.
- Establish stable JavaScript hooks.
- Add basic JavaScript.
- Send a request from the browser to FastAPI.
- Receive JSON.
- Display backend data in the page.

The frontend created during this phase should be simple but should NOT be considered disposable.

Learning focus:

- HTML
- CSS
- JavaScript
- DOM
- Event listeners
- fetch()
- HTTP
- REST
- JSON
- Frontend/backend communication

---

## Phase 3: Database

Introduce persistence.

Tasks may include:

- Configure SQLite.
- Create the initial database.
- Introduce required models/tables.
- Perform basic database operations.
- Inspect stored data.

Learning focus:

- SQL
- SQLite
- Relational databases
- Tables
- Primary keys
- Foreign keys
- Relationships
- Persistence
- CRUD

---

## Phase 4: Authentication

Implement user accounts.

Tasks may include:

- Registration
- Password hashing
- Login
- Password verification
- JWT creation
- Protected endpoints
- Authorization
- Logout behavior

Learning focus:

- Authentication
- Authorization
- Hashing
- Tokens
- JWT
- Protected API routes
- Security

---

## Phase 5: Gemini Integration

Add AI-generated study material.

Tasks may include:

- Obtain/configure the Gemini API key.
- Store the key securely using environment variables.
- Create the Gemini integration.
- Send a topic to Gemini.
- Request structured study material.
- Receive the response.
- Parse/validate the response.
- Return study material through FastAPI.
- Display it in the frontend.
- Handle common API failures.

Learning focus:

- External APIs
- API keys
- Environment variables
- JSON
- Prompts
- Error handling
- Service separation

---

## Phase 6: Saved Study Material

Allow generated material to persist.

Tasks may include:

- Save generated study material.
- Associate saved material with the authenticated user.
- Retrieve the user's saved topics.
- Open an individual saved topic.
- Display saved content.

Learning focus:

- SQL relationships
- Foreign keys
- Authentication plus database interaction
- Application architecture
- Data ownership

---

## Phase 7: Complete CRUD and Search

Implement:

- Create
- Read
- Update
- Delete
- Search

Users must only be able to modify their own data.

Learning focus:

- CRUD
- REST design
- SQL operations
- Authorization
- Search
- Error handling

---

## Phase 8: Frontend Polish

Only after core functionality is working, improve the presentation.

Possible improvements include:

- Dashboard styling
- Navigation
- Saved-note cards
- Study-material presentation
- Flashcard presentation
- Quiz presentation
- Account page
- Typography
- Spacing
- Responsive layout
- Loading indicators
- Empty states
- Error messages
- Accessibility improvements

Preserve existing JavaScript hooks and backend API contracts where practical.

Do not sacrifice working functionality merely for visual changes.

After meaningful frontend changes, retest affected features.

---

## Phase 9: Testing, Regression Testing, and Cleanup

Test complete workflows.

At minimum, verify behavior such as:

- Registration works
- Login works
- Logout works
- Authentication protection works
- Topic generation works
- AI output displays correctly
- Save works
- Saved material loads
- Search works
- Edit works
- Delete works
- Account information loads
- Users cannot access another user's data
- Loading states behave correctly
- Common errors are displayed appropriately

Fix regressions before moving on.

Remove dead code.

Refactor only when the change improves the project.

Learning focus:

- Debugging
- Testing
- Regression testing
- Refactoring
- Error handling

---

## Phase 10: Deployment

Prepare RecallAI for online deployment.

Tasks may include:

- Production configuration
- Render deployment
- Production environment variables
- Production database configuration
- PostgreSQL migration if appropriate
- Verify the deployed frontend/backend workflow

Learning focus:

- Deployment
- Cloud concepts
- Development vs production
- Environment configuration
- Production databases

---

## Phase 11: CI/CD

After the deployed application works:

- Introduce an appropriate GitHub Actions workflow.
- Automatically run useful tests/checks.
- Understand what triggers the workflow.
- Understand what happens when a workflow fails.

Learning focus:

- CI
- CD
- Automation
- GitHub Actions
- Build/test workflows

---

# 15. Learning Checkpoints

After implementing a meaningful feature, the developer should be able to answer:

1. What did we add?
2. Why does it exist?
3. Which files are involved?
4. What does each involved file do?
5. What happens when the feature runs?
6. What data enters the feature?
7. What data comes out?
8. Which other parts of RecallAI does it communicate with?
9. What could cause it to fail?
10. How could we investigate a failure?

Do not require the developer to memorize every line.

The developer should understand the flow well enough to confidently explain it.

---

# 16. LEARNING.md

LEARNING.md is a living study guide.

Update it throughout development based on concepts that have actually been implemented and understood.

Do NOT prefill it with explanations for technologies that have not been reached yet.

After a meaningful development phase, suggest useful concepts to document.

Entries should use examples from RecallAI whenever possible.

For example, rather than only defining POST abstractly, explain where RecallAI uses POST and what data is being sent.

Possible eventual topics include:

- FastAPI
- Client/server architecture
- HTTP
- REST
- JSON
- SQL
- CRUD
- Authentication
- Authorization
- Password hashing
- JWT
- Gemini
- External APIs
- Environment variables
- Deployment
- CI/CD

LEARNING.md should become useful interview-review material.

---

# 17. Git Practices

Use Git throughout development.

Prefer meaningful commits associated with real milestones.

Possible examples:

- Initialize FastAPI backend
- Connect frontend to API
- Add SQLite persistence
- Add user registration
- Implement JWT authentication
- Integrate Gemini study generation
- Add saved topics
- Implement topic CRUD
- Improve RecallAI interface
- Add deployment configuration

Do not make fake commits simply to make the history appear more impressive.

Do not commit:

- API keys
- Secrets
- .env files containing secrets
- Virtual environments
- Generated caches
- Other files that belong in .gitignore

---

# 18. Scope Control

These are possible future features, NOT MVP requirements:

- PDF upload
- Wikipedia integration
- YouTube transcript import
- Multiple AI providers
- AWS migration
- Docker
- Study-progress tracking
- Advanced analytics
- Recommendation systems
- Social features
- React or another frontend framework
- Mobile application
- Complex microservice architecture

Do not implement these unless explicitly requested.

Finish the core application first.

---

# 19. Rules for Codex Changes

When given a task, remain within the requested phase and feature.

Do not continue building later phases automatically.

Before making a large architectural change:

1. State what needs to change.
2. Explain why.
3. Identify the major files affected.
4. Prefer the smallest reasonable solution.

Do not silently rewrite unrelated working code.

Reuse existing code when reasonable.

If refactoring is necessary, explain the reason.

When multiple valid implementations exist, prefer the implementation that is:

- Easy to understand
- Secure
- Maintainable
- Appropriate for the current scale of RecallAI

Do not add complexity solely because it might be useful someday.

If introducing a new file, folder, dependency, technology, or architectural layer, there should be a clear current reason for it.

---

# 20. UI Change Safety

Visual improvements must not silently break working functionality.

When modifying existing frontend code:

1. Identify interactive elements affected by the change.
2. Preserve stable JavaScript hooks where practical.
3. Preserve existing API calls unless functionality requires changing them.
4. Update JavaScript deliberately if HTML structure changes.
5. Test affected interactions after the change.
6. Check for regressions in previously working features.

A visually polished page that breaks existing functionality is not considered an improvement.

---

# 21. Definition of Success

RecallAI Version 1 is successful when:

1. A user can register.
2. A user can log in and log out.
3. Authentication works securely.
4. A user can enter a study topic.
5. Gemini can generate useful study material.
6. The frontend displays generated material.
7. A user can save generated material.
8. Saved material persists in a relational database.
9. A user can view, search, edit, and delete their saved material.
10. Users cannot access another user's private material.
11. The interface is polished and usable.
12. The application can be deployed and accessed online.
13. Basic testing protects important functionality.
14. CI/CD is introduced after the core application is stable.
15. The developer can confidently explain how the major pieces work and communicate.

The final requirement is as important as the application functioning.

RecallAI should demonstrate genuine understanding rather than unnecessary complexity.