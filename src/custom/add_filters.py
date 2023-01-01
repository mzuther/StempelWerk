from src.StempelWerk import StempelWerk


class CustomCode(StempelWerk.CustomCodeTemplate):
    def __init__(self, copy_of_settings):
        super().__init__(copy_of_settings)


    def _display_environment_change(self, new, old, display_type):
        added = ['"' + s + '"' for s in sorted(new - old)]
        count = len(added)
        added = ', '.join(added)

        if self.settings.show_debug_messages:
            print(f'DEBUG:   - Added { count } { display_type }: { added }.')


    def update_environment(self, jinja_environment):
        jinja_environment = super().update_environment(
            jinja_environment)


        def uppercase_first(string):
            return string[0].upper() + string[1:].lower()


        def add_exclamation_mark(string, is_spanish=False):
            if is_spanish:
                string = '¡' + string
            return string + '!'


        old_filters = set(jinja_environment.filters)

        jinja_environment.filters["upper_first"] = uppercase_first
        jinja_environment.filters["add_exclamation_mark"] = add_exclamation_mark

        new_filters = set(jinja_environment.filters)
        self._display_environment_change(new_filters, old_filters, 'filters')

        return jinja_environment
