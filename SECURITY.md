# Security Policy

## Reporting a Vulnerability

If you discover a security vulnerability in this project, please report it responsibly:

1. **Open a GitHub Issue** — [Create an issue](https://github.com/DarrenJohns/djtools-rvtools-viz/issues/new) with the label `security`
2. **Email** — Contact the maintainer directly via GitHub profile

Please include:
- A description of the vulnerability
- Steps to reproduce the issue
- Any potential impact

## Scope

This is a client-side, single-file HTML application with **no backend, no authentication, and no user data storage**. All RVTools file parsing and analysis happens entirely in the browser. Uploaded `.xlsx` files never leave your machine.

## Response

Issues will be reviewed and addressed as soon as possible. Security fixes are deployed via the GitHub Actions pipeline once merged to `main`.
