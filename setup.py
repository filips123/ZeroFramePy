from setuptools import setup

def readme():
    with open('README.md') as f:
            return f.read()

setup(
    name = 'zeroframe-ws-client',
    description = 'ZeroFrame WebSocket API for Python',
    long_description = readme(),
    long_description_content_type='text/markdown',
    license = 'MIT',

    version_format = '{tag}',
    setup_requires = ['setuptools-git-version'],

    packages = ['zeroframe_ws_client'],

    install_requires = [
        'websocket-client>=0.56.0,<0.57.0',
    ],

    extras_require = {
        'lint': ['pylint'],
    },

    python_requires = '>= 3.5',

    author = 'Filip Š',
    author_email = 'projects@filips.si',
    url = 'https://github.com/filips123/ZeroFramePy/',
    keywords = 'zeronet, zeroframe, websocket, library, p2p, decentralized',

    classifiers = [
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Topic :: Communications',
        'Topic :: Internet',
        'Topic :: Software Development :: Libraries',
        'Topic :: Utilities',
    ],

    include_package_data = True,
)
