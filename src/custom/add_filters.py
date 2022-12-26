def update_environment(jinja_environment):

    def display_environment_change(new, old, display_type):
        added = ['"' + s + '"' for s in sorted(new - old)]
        count = len(added)
        added = ', '.join(added)

        print(f'CUSTOM: Added { count } { display_type }: { added }.')


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
    display_environment_change(new_filters, old_filters, 'filters')

    return jinja_environment


update_environment(jinja_environment)  # noqa: F821
