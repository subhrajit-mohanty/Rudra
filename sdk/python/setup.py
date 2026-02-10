from setuptools import find_packages, setup

setup(
    name="rudra",
    version="1.0.1",
    description="Python SDK for Rudra Auth Platform",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Rudra Contributors",
    license="MIT",
    url="https://github.com/rudra-auth/rudra",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=["requests>=2.28.0"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Topic :: Security",
        "Topic :: Internet :: WWW/HTTP",
    ],
)