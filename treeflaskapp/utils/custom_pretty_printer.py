from pprint import PrettyPrinter


class CustomPrettyPrinter(PrettyPrinter):
    def _format_dict_items(self, items, stream, indent, allowance, context, level):
        # Sort the items by key, with 'id' always first and 'name' second
        items = sorted(items, key=lambda x: (x[0] != 'id', x[0] != 'name', x[0]))
        PrettyPrinter._format_dict_items(self, items, stream, indent, allowance, context, level)


# Usage:
if __name__ == "__main__":
    pp = CustomPrettyPrinter()
    logger.info(f'persons_data: \n{pp.pformat(persons_data)}')
