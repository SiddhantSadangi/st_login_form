from pathlib import Path

import setuptools

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")


def get_version(rel_path):
    with open(rel_path, "r", encoding="UTF-8") as f:
        for line in f:
            if line.startswith("__version__"):
                delim = '"' if '"' in line else "'"
                return line.split(delim)[1]
    raise RuntimeError("Unable to find version string.")


setuptools.setup(
    name="st-login-form",
    version=get_version("src/st_login_form/__init__.py"),
    url="https://github.com/SiddhantSadangi/st_login_form",
    author="Siddhant Sadangi",
    author_email="siddhant.sadangi@gmail.com",
    description="A streamlit component that creates customizable user authentication forms connected to a Supabase DB. It lets users create a new username and password, login to an existing account, or login as an anonymous guest.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    project_urls={
        "Documentation": "https://github.com/SiddhantSadangi/st_login_form/blob/main/README.md",
        "Funding": "https://www.buymeacoffee.com/siddhantsadangi",
    },
    packages=setuptools.find_packages(where="src"),
    package_dir={"": "src"},
    include_package_data=True,
    classifiers=[
        "Environment :: Plugins",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Security",
        "Topic :: Software Development :: User Interfaces",
    ],
    keywords=["streamlit", "login", "authentication", "supabase"],
    python_requires=">=3.9",
    install_requires=[
        "streamlit>=1.2",
        "jinja2>=3.1.6",
        "st_supabase_connection>=2.0",
        "argon2-cffi>=23.1.0",
    ],
)
