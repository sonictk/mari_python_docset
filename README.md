# Readme

This is a [Dash](http://kapeli.com/dash)-compatible docset for the Foundry's
Mari Python API reference. It has been built against the 4.0v1 documentation,
but should work for other versions as well.


## Usage

Place the ``mari-401-python-api.docset`` folder in your directory that is 
used by Zeal/Dash/Velocity to lookup docsets. Please refer to your respective
application's documentation for how to install such things.


## Building

### Dependencies

You will need to install the dependencies listed in ``requirements.txt``
through ``pip`` or have it available on your ``PYTHONPATH``.

### Generating the docset

The Python scripts for building the database and formatting the documentation
to work in standalone mode are located in the ``scripts`` directory. The Mari 
documentation should be placed in a directory called ``pydoc``.  Once that is
done, you should be able to run ``python clean_html_documentation.py`` and 
``python generate_database_entries.py`` in order to re-generate the docset. You 
can also specify the location of the source documenation using the ``-i`` flag.


## License

Except for the documentation itself (which belongs to The Foundry and is freely
available for download via their website), the license for the scripts in this
repository is viewable in the ``LICENSE`` file.


## Author
Siew Yi Liang
