# Copyright 2016-2018 Dirk Thomas
# Copyright 2021 Ruffin White
# Licensed under the Apache License, Version 2.0

import os
import os.path
from pathlib import Path

from colcon_clean.base_handler \
    import add_base_handler_arguments, get_base_handler_extensions
from colcon_clean.subverb \
    import clean_paths, CleanSubverbExtensionPoint
from colcon_core.argument_parser.destination_collector \
    import DestinationCollectorDecorator
from colcon_core.event_handler import add_event_handler_arguments
from colcon_core.plugin_system import satisfies_version
from colcon_core.verb import check_and_mark_build_tool
from colcon_core.verb import logger


class WorkspaceCleanSubverb(CleanSubverbExtensionPoint):
    """Clean current workspace."""

    def __init__(self):  # noqa: D107
        super().__init__()
        satisfies_version(
            CleanSubverbExtensionPoint.EXTENSION_POINT_VERSION, '^1.0')

    def add_arguments(self, *, parser):  # noqa: D102
        parser.add_argument(
            '--base-select', nargs='*', metavar='BASE_NAME',
            default=sorted(get_base_handler_extensions().keys()),
            help='Select base names to clean in workspace '
                 '(default: [build, install, log, test_result])')

        parser.add_argument(
            '-y', '--yes',
            action='store_true',
            help='Automatic yes to prompts')
        add_base_handler_arguments(parser)
        add_event_handler_arguments(parser)

        decorated_parser = DestinationCollectorDecorator(parser)
        self.task_argument_destinations = decorated_parser.get_destinations()

    def main(self, *, context):  # noqa: D102
        check_and_mark_build_tool(context.args.build_base)

        base_handler_extensions = get_base_handler_extensions()
        base_paths = set()

        args = context.args

        for base_name in args.base_select:
            if base_name in base_handler_extensions:
                base_handler_extension = base_handler_extensions[base_name]
                workspace_paths = \
                    base_handler_extension.get_workspace_paths(args=args)
                for workspace_path in workspace_paths:
                    workspace_path = Path(os.path.abspath(workspace_path))
                    base_paths.add(workspace_path)
            else:
                logger.warning(
                    "No base handler for selction '{base_name}'"
                    .format_map(locals()))

        confirmed = args.yes
        clean_paths(base_paths, confirmed)

        return 0
