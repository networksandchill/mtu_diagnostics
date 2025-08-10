from setuptools import setup, find_packages

setup(
    name="mtu_diagnostics",
    version="0.1.0",
    description="Network MTU size detection and diagnostic tool",
    packages=find_packages(),
    install_requires=[
        "psutil",
        "click",
    ],
    entry_points={
        "console_scripts": [
            "mtu-diag=cli:main",
        ],
    },
    python_requires=">=3.7",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Topic :: System :: Networking",
    ],
)
