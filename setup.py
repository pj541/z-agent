import setuptools

# VERSION = '{{VERSION_PLACEHOLDER}}'
setuptools.setup(
    name="z-agent",
    version="0.1.0.2",
    author="Prajwal",
    author_email="pkumarjha@zscaler.com",
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=["websockets", "asyncio"],
    packages=setuptools.find_packages(),
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "z-agent = z_agent.cli:main",
        ]
    }
)
