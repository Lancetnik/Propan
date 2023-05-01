# DOCS

### How to help

You will be of invaluable help if you contribute to the documentation.

Such a contribution can be:

* Indications of inaccuracies, errors, typos
* Suggestions for editing individual sections
* Making additions

You can report all this in [discussions] (https://github.com/Lancetnik/Propan/discussions ) on GitHub, start [issue](https://github.com/Lancetnik/Propan/issues ), or write about it in our [telegram](https://t.me/propan_python ) the group.

!!! note
    Special thanks to those who are ready to offer help with the case and help in ** developing documentation **, as well as translating it into ** other languages**.

### How to get started

To develop the documentation, you don't even need to install the entire **Propan** project as a whole.

Enough:

1. Clone the project repository
2. Go to the `docs/` directory
3. Create a virtual environment
    ```bash
    python -m venv venv
    ```
4. Activate it
    ```bash
    source venv/bin/activate
    ```
5. Install documentation dependencies
    ```bash
    pip install -r requirements.txt
    ```
6. Start the local documentation server
    ```bash
    mkdocs serve
    ```

Now all changes in the documentation files will be reflected on your local version of the site.
After making all the changes, you can issue a `PR` with them - and I will gladly accept it!