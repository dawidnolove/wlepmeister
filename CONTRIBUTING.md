# Contributing to Wlepmeister
Thank you for considering contributing to this project.
wlepmeister is a focused, technical tool — contributions should stay clean, scoped, and purposeful.

## Before You Start
## Open an Issue
Always start by creating an Issue describing:
* what you want to change
* why it matters
* how you plan to implement it

This prevents duplicated work and keeps the roadmap clear.

## Project Expectations
By contributing, you agree to follow the project’s Code of Conduct.
See: [CODE_OF_CONDUCT.md](https://github.com/dawidnolove/wlepmeister/blob/main/CODE_OF_CONDUCT.md)

## How to Contribute
## 1. Fork and Branch
* Fork the repository
* Create a feature branch:
``` txt
git checkout -b feature/your-change
```
* Keep branches small and focused on a single task

## 2. Code Style
* Python 3.10+
* Keep functions short and explicit
* Avoid unnecessary dependencies
* Prefer clarity over cleverness
* Add comments only where logic is non‑obvious (especially image processing)

$ 3. Commit Messages
Use clear, meaningful commit messages:
``` txt
Fix poster rendering bug (##12)
Add CLI flag for output size (##18)
Refactor color parser
```
To auto‑close an Issue:
``` txt
Fixes ##ID
```
## 4. Pull Requests
A good PR includes:
* a clear description
* reference to the Issue
* screenshots if visual output changed
* minimal, focused changes
PRs mixing unrelated changes will be rejected.

## 5. Tests (Optional but Encouraged)
If your change affects core logic, add:
* a simple test
* or an example script demonstrating the behavior

## What You Can Work On
* bug fixes
* CLI improvements
* documentation
* performance tweaks
* dependency security issues (Pillow, filelock, dotenv, etc.)
* small, self‑contained features

## Asking Questions
If you’re unsure about anything:
* open an Issue
* or start a Discussion
* Both are welcome.

## License
By contributing, you agree that your contributions will be licensed under the repository’s license.
