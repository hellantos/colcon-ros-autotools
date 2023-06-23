# colcon-ros-autotools

An extension for [colcon-core](https://github.com/colcon/colcon-core) to support [Gnu Autotools](https://www.gnu.org/software/automake/manual/html_node/Autotools-Introduction.html) projects.

## Features

For all packages with `configure.ac` and `package.xml` files:

- `colcon build` will call `autoreconf -i`, `./configure`, and `make install`

## Try it out

### Using pip

```
pip install -U colcon-ros-autotools
```

### From source

Follow the instructions at https://colcon.readthedocs.io/en/released/developer/bootstrap.html, except in "Fetch the sources" add the following to `colcon.repos`:

```yaml
  colcon-ros-autotools:
    type: git
    url: https://github.com/colcon/colcon-ros-autotools.git
    version: main
```

After that, run the `local_setup` file, build any colcon workspace with autotools projects in it, and report any issues!
