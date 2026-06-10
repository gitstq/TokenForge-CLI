from setuptools import setup, find_packages

setup(
    name="tokenslim",
    version="1.0.0",
    description="Lightweight Terminal LLM Token Intelligent Compression Engine",
    author="gitstq",
    license="MIT",
    python_requires=">=3.8",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "tokenslim=tokenslim:main",
        ],
    },
)
