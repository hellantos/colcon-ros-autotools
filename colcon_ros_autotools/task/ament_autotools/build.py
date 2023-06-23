# Copyright 2018 Esteve Fernandez
# Licensed under the Apache License, Version 2.0

from distutils import dir_util
import glob
import os
from pathlib import Path
import shutil

from colcon_core.environment import create_environment_scripts
from colcon_core.logging import colcon_logger
from colcon_core.plugin_system import satisfies_version
from colcon_core.shell import create_environment_hook
from colcon_core.shell import get_command_environment
from colcon_core.task import run
from colcon_core.task import TaskExtensionPoint
from colcon_cmake.task.cmake import which_executable
from argparse import ArgumentParser


logger = colcon_logger.getChild(__name__)


class AutotoolsBuildTask(TaskExtensionPoint):
    """Build autotools packages."""

    def __init__(self):  # noqa: D107
        super().__init__()
        satisfies_version(TaskExtensionPoint.EXTENSION_POINT_VERSION, '^1.0')

    def add_arguments(self, *, parser: ArgumentParser):  # noqa: D102
        parser.add_argument("--features", nargs="*", default=str.lstrip, help="Features to enable or disable. Write enable-[feature] to enable or disable-[feature] to disable.")
        pass

    async def build(  # noqa: D102
        self, *, additional_hooks=None, skip_hook_creation=False
    ):
        pkg = self.context.pkg
        args = self.context.args

        logger.info(
            "Building autotools package in '{args.path}'".format_map(locals()))

        if additional_hooks is None:
            additional_hooks = []

        try:
            env = await get_command_environment(
                'build', args.build_base, self.context.dependencies)
        except RuntimeError as e:
            logger.error(str(e))
            return 1

        rc = await self._reconfigure(args, env)
        if rc and rc.returncode:
            return rc.returncode
        
        configure_executable: Path = Path(args.path).joinpath('configure')
        if not configure_executable.is_file():
            logger.error("No configure script found in '{args.path}'".format_map(locals()))
            return 1

        rc = await self._configure(str(configure_executable), args, env)
        if rc and rc.returncode:
            return rc.returncode

        rc = await self._build(args, env)
        if rc and rc.returncode:
            return rc.returncode
        
        if not skip_hook_creation:
            create_environment_scripts(
                pkg, args, additional_hooks=additional_hooks)

    async def _reconfigure(self, args, env):
        self.progress('reconfigure')
        autoreconf_executable = which_executable('AUTORECONF', 'autoreconf')
        autoreconf_args = []
        autoreconf_args += ['-i']
        autoreconf_args += [args.path]
        completed = await run(self.context, [autoreconf_executable] + autoreconf_args, cwd=args.build_base, env=env)
        return completed


    async def _configure(self, configure_file, args, env):
        self.progress('configure')
        conf_args = []
        conf_args += ['--prefix=' + args.install_base]
        conf_args += (args.features or [])
        completed = await run(self.context, [configure_file] + conf_args, cwd=args.build_base, env=env)
        return completed

    async def _build(self, args, env):
        self.progress('build')
        make_executable = which_executable('MAKE', 'make')
        completed = await run(self.context, [make_executable, 'install'], cwd=args.build_base, env=env)
        return completed
