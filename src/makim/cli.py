"""Cli functions to define the arguments and to call Makim."""
import argparse
import os
import sys

from pathlib import Path

from makim import Makim, __version__


SUBCOMMANDS = (
    'cron',
)

class CustomHelpFormatter(argparse.RawTextHelpFormatter):
    """Formatter for generating usage messages and argument help strings.

    Only the name of this class is considered a public API. All the methods
    provided by the class are considered an implementation detail.
    """

    def __init__(
        self,
        prog,
        indent_increment=2,
        max_help_position=4,
        width=None,
        **kwargs,
    ):
        """Define the parameters for the argparse help text."""
        super().__init__(
            prog,
            indent_increment=indent_increment,
            max_help_position=max_help_position,
            width=width,
            **kwargs,
        )


makim = Makim()


def _get_args(subcommand=None):
    """
    Define the arguments for the CLI.

    note: when added new flags, update the list of flags to be
          skipped at extract_makim_args function.
    """
    makim_file_default = str(Path(os.getcwd()) / '.makim.yaml')

    parser = argparse.ArgumentParser(
        prog='Makim',
        description=(
            'Makim is a tool that helps you to organize '
            'and simplify your helper commands.'
        ),
        epilog=(
            'If you have any problem, open an issue at: '
            'https://github.com/osl-incubator/makim'
        ),
        add_help=False,
        formatter_class=CustomHelpFormatter,
    )
    parser.add_argument(
        '--help',
        '-h',
        action='store_true',
        help='Show the help menu',
    )

    parser.add_argument(
        '--version',
        action='store_true',
        help='Show the version of the installed Makim tool.',
    )

    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Show the commands to be executed.',
    )

    parser.add_argument(
        '--dry-run',
        action='store_true',
        help="Show the commands but don't execute them.",
    )

    parser.add_argument(
        '--makim-file',
        type=str,
        default=makim_file_default,
        help='Specify a custom location for the makim file.',
    )

    try:
        idx = sys.argv.index('--makim-file')
        makim_file = sys.argv[idx + 1]
    except ValueError:
        makim_file = makim_file_default

    makim.load(makim_file)
    config_data = makim.global_data
    target_help = []

    groups = config_data.get('groups', [])
    for group in groups:
        target_help.append('\n' + group + ':')
        target_help.append('-' * (len(group) + 1))
        for target_name, target_data in groups[group]['targets'].items():
            target_name_qualified = f'{group}.{target_name}'
            help_text = target_data['help'] if 'help' in target_data else ''
            target_help.append(f'  {target_name_qualified} => {help_text}')

            if 'args' in target_data:
                target_help.append('    ARGS:')

                for arg_name, arg_data in target_data['args'].items():
                    target_help.append(
                        f'      --{arg_name}: ({arg_data["type"]}) '
                        f'{arg_data["help"]}'
                    )
    
    # Process cron configuration
    cron_jobs = config_data.get('cron', {})
    if cron_jobs:
        target_help.append('\nMakim cron jobs:')
        for job_name, job_data in cron_jobs.items():
            target_help.append('\n' + job_name + ':')
            target_help.append('-' * (len(job_name) + 1))
            help_text = job_data.get('help', 'N/A')
            target_help.append(f'  help: {help_text}')
            schedule = job_data.get('schedule', 'N/A')
            target_help.append(f'  schedule: {schedule}')
            target = job_data.get('target', 'N/A')
            target_help.append(f'  target: {target}')
        target_help.append('\n')

    parser.add_argument(
        'target',
        nargs='?',
        default=None,
        help=(
            'Specify the target command to be performed. Options are:\n'
            + '\n'.join(target_help)
        ),
    )

    return parser


def _get_args_with_subcommands():
    parser = _get_args()
    
    # add subparsers for subcommands
    # TODO: refactor, this function should be removed and
    # conditionally injected inside _get_args() based
    # on the subcommand passed (sys.argsv[1] in SUBCOMMANDS)
    cron_subparsers = parser.add_subparsers(title='Makim cron commands', dest='cron_command', metavar='', help='\nMakim can run, create and manage makim commands as cron jobs\n\n')

    # return help when no subcommand is specified
    cron_parser = cron_subparsers.add_parser('cron', help='show help message\n\n')
    cron_parser.set_defaults(cron_command='help')

    # run
    run_command = cron_subparsers.add_parser('run', help='runs cron job the same as makim group.target\n\n')
    run_command.add_argument('job', type=str, help='Name of the cron job to run')

    # list
    list_command = cron_subparsers.add_parser('list', help='lists all cron jobs\n\n')
    list_command.add_argument('job', type=str, help='Name of the cron job to run')

    # instal
    install_command = cron_subparsers.add_parser('install', help='installs cron job\n\n')
    install_command.add_argument('job', type=str, help='Name of the cron job to be installed')

    return parser



def show_version():
    """Show version."""
    print(__version__)


def extract_makim_args():
    """Extract makim arguments from the CLI call."""
    makim_args = {}
    index_to_remove = []
    for ind, arg in enumerate(list(sys.argv)):
        if arg in [
            '--help',
            '--version',
            '--verbose',
            '--makim-file',
            '--dry-run',
        ]:
            continue

        if not arg.startswith('--'):
            continue

        index_to_remove.append(ind)

        arg_name = None
        arg_value = None

        next_ind = ind + 1

        arg_name = sys.argv[ind]

        if (
            len(sys.argv) == next_ind
            or len(sys.argv) > next_ind
            and sys.argv[next_ind].startswith('--')
        ):
            arg_value = True
        else:
            arg_value = sys.argv[next_ind]
            index_to_remove.append(next_ind)

        makim_args[arg_name] = arg_value

    # remove exclusive makim flags from original sys.argv
    for ind in sorted(index_to_remove, reverse=True):
        sys.argv.pop(ind)

    return makim_args


def app():
    """Call the makim program with the arguments defined by the user."""
    print(sys.argv)
    print(len(sys.argv))
    print(sys.argv[1])
    # TODO: inject subcommand conditionally based on sys.argv[1] in _get_args() and remove _get_args_with_subcommands()
    if len(sys.argv) > 1 and any(subcommand == sys.argv[1] for subcommand in SUBCOMMANDS):
        args_parser = _get_args_with_subcommands()
    else:
        args_parser = _get_args()

    makim_args = extract_makim_args()
    args = args_parser.parse_args()

    if args.version:
        return show_version()

    if not args.target or args.help:
        args_parser = _get_args_with_subcommands()
        return args_parser.print_help()

    if args.help:
        return args_parser.print_help()

    makim.load(args.makim_file)
    makim_args.update(dict(args._get_kwargs()))
    return makim.run(makim_args)
