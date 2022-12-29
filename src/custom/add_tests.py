def update_environment(jinja_environment, show_debug_messages):

    def display_environment_change(new, old, display_type):
        added = ['"' + s + '"' for s in sorted(new - old)]
        count = len(added)
        added = ', '.join(added)

        if show_debug_messages:
            print(f'DEBUG: Added { count } { display_type }: { added }.')


    def is_spanish(string):
        return 'este es' in string


    old_tests = set(jinja_environment.tests)

    jinja_environment.tests["spanish"] = is_spanish

    new_tests = set(jinja_environment.tests)
    display_environment_change(new_tests, old_tests, 'tests')

    return jinja_environment


update_environment(jinja_environment, show_debug_messages)  # noqa: F821
