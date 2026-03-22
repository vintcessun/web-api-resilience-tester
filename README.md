# Web API Resilience Tester

A high-fidelity tool designed to test the robustness and anomaly handling capabilities of PHP-based web interfaces under simulated high-concurrency and diverse data input scenarios.

## Overview

This project provides a Python-based automation system to simulate realistic user interactions with web APIs. It is specifically engineered to test how backend systems handle a large volume of "poisoned" or randomized data across multiple simulated platforms.

## Key Features

- **Multi-Platform Data Mimicry**: Generates high-fidelity account data for platforms like QQ, WeChat, and Potato.
- **Advanced Password Simulation**: Uses a weighted randomization strategy to generate common weak passwords, name-pinyin combinations, phone numbers, birthdays, and keyboard sequences.
- **Anti-Bot Evasion**:
  - Randomized sleep intervals between requests.
  - Dynamic User-Agent rotation.
  - X-Forwarded-For IP spoofing using common Chinese public IP ranges.
- **GitHub Actions Integration**: Automated execution via Cron schedules or manual triggers.
- **Resilience Handling**: Gracefully exits upon encountering server-side errors (502/504) or timeouts to avoid resource waste.

## Setup & Configuration

### Environment Variables

The script requires the following environment variables, which should be configured as GitHub Secrets for the Action:

- `TARGET_URL`: The destination API endpoint.
- `REFERER_URL`: The referer header to be used for requests.

### Usage

1. Clone the repository.
2. Install dependencies: `pip install -r requirements.txt`.
3. Set the required environment variables.
4. Run the script: `python main.py`.

## Disclaimer

This tool is for educational and authorized testing purposes only. The author is not responsible for any misuse or damage caused by this tool.
