from src.StempelWerk import StempelWerk


class CustomCode(StempelWerk.CustomCodeTemplate):
    def __init__(self, copy_of_settings, printer):
        super().__init__(copy_of_settings, printer)


    def _display_environment_change(self, new, old, display_type):
        added = ['"' + s + '"' for s in sorted(new - old)]
        count = len(added)
        added = ', '.join(added)
        self.print_debug(f'  - Added { count } { display_type }: { added }.')


    def update_environment(self, jinja_environment):
        jinja_environment = super().update_environment(
            jinja_environment)


        def is_spanish(string):
            return 'este es' in string


        old_tests = set(jinja_environment.tests)

        jinja_environment.tests["spanish"] = is_spanish

        new_tests = set(jinja_environment.tests)
        self._display_environment_change(new_tests, old_tests, 'tests')

        return jinja_environment
