# Contribution Guide

Welcome to the radio-active project! We're thrilled that you want to contribute. Before you get started, please take a moment to read this guide to understand our contribution process.


## Getting Started

To get started, make sure you have `git`, `ffmpeg` and `python3` installed on your local machine. You'll also need a GitHub account.

## How to Contribute

### Fork the Repository

1. Click the "Fork" button on the top right of this repository's page.
2. This will create a copy of the repository in your GitHub account.

### Clone Your Fork

1. Clone your fork to your local machine using the following command:
   ```bash
    git clone https://github.com/deep5050/radio-active.git
    git checkout -b your-branch-name
   ```

### Install dependencies
```bash
pip3 install -r requirements.txt
pip3 install -r requirements-dev.txt
```

### Make changes.

Modify the code as required

### Test Your Changes

Before submitting your changes, please ensure that your code doesn't break the existing functionality.

Run `make` to install it locally and test before you push changes!

   ```
   git add .
   git commit -m "Add your commit message here" --signoff
   git push
   ```
### Create a Pull Request
Visit the original repository on GitHub.
You should see a "New Pull Request" button. Click on it.
Follow the instructions to create your pull request.

Fill the description section with meaningful message.

