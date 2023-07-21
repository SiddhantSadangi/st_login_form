from pathlib import Path

import setuptools

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setuptools.setup(
    name="st-login-form",
    version="0.3.0",
    url="https://github.com/SiddhantSadangi/st_login_form",
    author="Siddhant Sadangi",
    author_email="siddhant.sadangi@gmail.com",
    description="A streamlit component that creates a user login form connected to a Supabase DB. It lets users create a new username and password, login to an existing account, or login as an anonymous guest.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    project_urls={
        "Documentation": "https://github.com/SiddhantSadangi/st_login_form/blob/main/README.md",
        "Support": "https://www.buymeacoffee.com/siddhantsadangi",
    },
    packages=setuptools.find_packages(where="src"),
    package_dir={"": "src"},
    include_package_data=True,
    classifiers=[
        "Environment :: Plugins",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: User Interfaces",
    ],
    keywords=["streamlit", "login"],
    python_requires=">=3.8",
    install_requires=["streamlit>=1.2", "jinja2", "supabase"],
)
