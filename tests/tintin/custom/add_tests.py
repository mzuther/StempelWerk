import jinja2

from stempelwerk.StempelWerk import StempelWerk


class CustomCode(StempelWerk.CustomCodeTemplate):
    def __init__(
        self,
        copy_of_settings: 'StempelWerk.Settings',
        printer: 'StempelWerk.LinePrinter',
    ) -> None:
        super().__init__(copy_of_settings, printer)

    def _display_environment_change(
        self,
        new_environment: set[str],
        old_environment: set[str],
        display_type: str,
    ) -> None:
        differences = sorted(new_environment - old_environment)

        added = ['"' + difference + '"' for difference in differences]
        count = len(added)
        added_string = ', '.join(added)

        self.print_debug(f'  - Added {count} {display_type}: {added_string}.')

    def update_environment(
        self,
        jinja_environment: jinja2.environment.Environment,
    ) -> jinja2.environment.Environment:
        jinja_environment = super().update_environment(
            jinja_environment,
        )

        def is_spanish(
            string: str,
        ) -> bool:
            return 'este es' in string

        old_tests = set(jinja_environment.tests)

        jinja_environment.tests['spanish'] = is_spanish

        new_tests = set(jinja_environment.tests)
        self._display_environment_change(
            new_tests,
            old_tests,
            'tests',
        )

        return jinja_environment
