# cjlang
Pure Python Cangjie parser and tools.

Reference material for this repository: [Cangjie Programming Language Specification](https://developer.huawei.com/consumer/cn/doc/cangjie-guides-V5/cj-lan-spec-V5)

## Installation

### Method 1: With pip

```bash
pip install cjlang
```

or:

```bash
pip install git+https://github.com/jstzwj/cjlang.git 
```

### Method 2: From source

1. Clone this repository
```bash
git clone https://github.com/jstzwj/cjlang.git
cd cjlang
```

2. Install the Package
```bash
pip install --upgrade pip
pip install -e .
```


## Usage

Here is a simple example demonstrating how to use `cjlang`:

```python
from cjlang import CangjieParser

parser = CangjieParser()
result = parser.parse("your_cangjie_input_here")
print(result)
```

## Contributing

If you want to contribute to this project, please feel free to submit a pull request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
