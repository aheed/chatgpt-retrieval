# chatgpt-retrieval

Simple script to use ChatGPT on your own files.

Here's the [YouTube Video](https://youtu.be/9AXP7tCI9PI).

## Installation

Install [Langchain](https://github.com/hwchase17/langchain) and other required packages.
```
pip install langchain openai chromadb tiktoken unstructured
```
Modify `constants.py.default` to use your own [OpenAI API key](https://platform.openai.com/account/api-keys), and to use you own [Portkey API key](https://app.portkey.ai/) rename it to `constants.py`.


Place your own python project into `data/`.

## Example usage
Test reading python files.
```
> python chatgpt.py "Is the class Galaxy immutable?"
No, the Galaxy class is not immutable.
```
