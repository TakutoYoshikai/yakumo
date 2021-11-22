from setuptools import setup, find_packages

setup(
    name = 'yakumo',
    version = '1.0.0',
    url = 'https://github.com/TakutoYoshikai/yakumo.git',
    license = 'MIT LICENSE',
    author = 'Takuto Yoshikai',
    author_email = 'takuto.yoshikai@gmail.com',
    description = 'yakumo is a steganography tool.',
    install_requires = ['setuptools', "pillow"],
    packages = find_packages(),
    entry_points={
        "console_scripts": [
            "yakumo = yakumo.yakumo:main",
        ]
    }
)
