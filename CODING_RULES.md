# Coding Rules and Guidelines

This document outlines the coding standards and practices to follow when working on this project.

## Testing and Server Management

- **After making changes, ALWAYS make sure to start up a new server so I can test it.**
- **Always kill all existing related servers that may have been created in previous testing before trying to start a new server.**

## Code Evolution and Patterns

- **Always look for existing code to iterate on instead of creating new code.**
- **Do not drastically change the patterns before trying to iterate on existing patterns.**
- **When fixing an issue or bug, do not introduce a new pattern or technology without first exhausting all options for the existing implementation. And if you finally do this, make sure to remove the old implementation afterwards so we don't have duplicate logic.**
- **Avoid making major changes to the patterns and architecture of how a feature works, after it has shown to work well, unless explicitly instructed.**

## Code Quality and Organization

- **Always prefer simple solutions.**
- **Avoid duplication of code whenever possible, which means checking for other areas of the codebase that might already have similar code and functionality.**
- **Keep the codebase very clean and organized.**
- **Avoid having files over 200-300 lines of code. Refactor at that point.**
- **Write thorough tests for all major functionality.**

## Environment Considerations

- **Write code that takes into account the different environments: dev, test, and prod.**
- **Mocking data is only needed for tests, never mock data for dev or prod.**
- **Never add stubbing or fake data patterns to code that affects the dev or prod environments.**

## Scope and Safety

- **You are careful to only make changes that are requested or you are confident are well understood and related to the change being requested.**
- **Never overwrite my .env file without first asking and confirming.**
- **Focus on the areas of code relevant to the task.**
- **Do not touch code that is unrelated to the task.**
- **Always think about what other methods and areas of code might be affected by code changes.**

## Scripts and Automation

- **Avoid writing scripts in files if possible, especially if the script is likely only to be run once.**

## Summary

These rules emphasize:
1. **Safety first** - Always test changes and be careful about scope
2. **Simplicity** - Prefer simple solutions and avoid unnecessary complexity
3. **Consistency** - Build on existing patterns rather than introducing new ones
4. **Quality** - Keep code clean, organized, and well-tested
5. **Environment awareness** - Consider dev, test, and prod implications
6. **Impact awareness** - Think about how changes affect other parts of the codebase
