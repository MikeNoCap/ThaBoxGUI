import setuptools

#with open("README.md", "r", encoding="utf-8") as fh:
long_description = "Nothing here at the moment..."

setuptools.setup(
    name='thabox',
    version='0.1.5',
    author='MikeNoCap',
    author_email='thorvaldsenmikkel@gmail.com',
    description="""ThaBox is an open-source and retro-modern chat application where clients can connect to chatrooms and talk anonymously.""",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/MikeNoCap/ThaBoxGUI',
    project_urls = {
        "Bug Tracker": "https://github.com/MikeNoCap/ThaBoxGUI/issues"
    },
    license='MIT',
    packages=['thabox'],
    install_requires=["python-socketio-client~=1.1", "python-socketio~=5.3", "keyboard~=0.13", "rich~=10.6", "playsound", "uvicorn", "aiohttp", "pillow"],
    entry_points = {
        'console_scripts': ['thabox=thabox.main:start'],
    }
)