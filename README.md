# chatgpt-retrieval

Simple script to use ChatGPT on your own files.

Here's the [YouTube Video](https://youtu.be/9AXP7tCI9PI).

## Installation

Install [Langchain](https://github.com/hwchase17/langchain) and other required packages.
```shell
pip install langchain langchain-community langchain-openai openai chromadb tiktoken unstructured
```
Modify `constants.py.default` to use your own [OpenAI API key](https://platform.openai.com/account/api-keys), and to use you own [Portkey API key](https://app.portkey.ai/) rename it to `constants.py`.


Place your own python project into `data/`.

## Example usage
Test reading python files.
```shell
python chatgpt.py "Is the class Galaxy immutable?"
No, the Galaxy class is not immutable.
```

### Warning printouts
At the moment you get warnings like
```
LangChainDeprecationWarning: The class `langchain_community.embeddings.openai.OpenAIEmbeddings` was deprecated in langchain-community 0.1.0 and will be removed in 0.2.0.
...
```
No obvious solution for now. See https://github.com/langchain-ai/langchain/discussions/15839

#### Workaround
Suppress stderr:
```shell
python chatgpt.py "Is the class Galaxy immutable?" 2> /dev/null
```