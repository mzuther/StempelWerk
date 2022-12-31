from src.StempelWerk import StempelWerk


class CustomCode(StempelWerk.CustomCodeTemplate):
    def __init__(self, copy_of_settings, show_debug_messages):
        super().__init__(copy_of_settings, show_debug_messages)


    def _display_environment_change(self, new, old, display_type):
        added = ['"' + s + '"' for s in sorted(new - old)]
        count = len(added)
        added = ', '.join(added)

        if self.show_debug_messages:
            print(f'DEBUG: Added { count } { display_type }: { added }.')


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
