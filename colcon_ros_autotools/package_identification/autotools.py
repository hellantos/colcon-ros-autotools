# Copyright 2018 Esteve Fernandez
# Licensed under the Apache License, Version 2.0

import os
from pathlib import Path
import pathlib
import re

from colcon_core.package_identification \
    import PackageIdentificationExtensionPoint
from colcon_ros.package_identification.ros import _get_package
from colcon_core.plugin_system import satisfies_version


class AutotoolsPackageIdentification(PackageIdentificationExtensionPoint):
    """Identify ament_autotools packages with `configure.ac` file and `package.xml` file."""
    PRIORITY = 160
    
    def __init__(self):  # noqa: D107
        super().__init__()
        satisfies_version(
            PackageIdentificationExtensionPoint.EXTENSION_POINT_VERSION,
            '^1.0')

    def identify(self, metadata):  # noqa: D102
        if metadata.type is not None and metadata.type != 'ament_autotools':
            return

        # Check for configure.ac
        configure_ac_path = pathlib.Path(metadata.path).joinpath('configure.ac')
        if not configure_ac_path.is_file():
            return

        package_xml_path = pathlib.Path(metadata.path).joinpath('package.xml')
        if not configure_ac_path.is_file():
            return

        metadata.type = 'ament_autotools'
        
        pkg = _get_package(str(metadata.path))
        print(pkg)

        if metadata.name is None:
            metadata.name = pkg['name']
        metadata.dependencies['build'] = {dep.name for dep in pkg.build_depends}
        metadata.dependencies['run'] = {dep.name for dep in pkg.run_depends}
        metadata.dependencies['test'] = {dep.name for dep in pkg.test_depends}