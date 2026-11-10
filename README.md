# Learn With Communities - Campaign Tracker

A fast, robust Terminal UI (TUI) tool designed to track student progress for the Google Skills Learn With Communities campaign. Built with Python and the Rich library, this tool scrapes public Google Skills Boost profiles to verify badge completions while ensuring operational stability through rate-limiting and secure error handling.

## Features
- **Terminal UI (TUI):** Clean, responsive progress bars and status tables powered by `rich`.
- **Rate Limiting:** Built-in configurable delays between requests to prevent IP blocking and server overload.
- **Graceful Error Handling:** Catches HTTP timeouts, dead links, and network exceptions without interrupting the batch process.
- **Input Validation:** Verifies URL structures to prevent processing malformed or malicious inputs.

## Prerequisites
- Python 3.8 or higher
- Git

## Installation

1. Clone the repository:
   ```bash
   git clone [https://github.com/banirudhak/gdg-campaign-tracker.git](https://github.com/banirudhak/gdg-campaign-tracker.git)
   cd gdg-campaign-tracker