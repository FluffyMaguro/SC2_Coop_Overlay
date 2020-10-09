import re

class InsideSearch():
    """ Class for searching of things inside a data structure."""

    def search(self, structure, *args):
        """
        Search for args in structure 
        Returns `found`, `args_found`

        `found` is True if all args were found, False otherwise
        `args_found` is a set of things that were successfully found

        """

        self.args_found = set()
        self.includes(structure, *args)
        found = True if len(args) == len(self.args_found) else False
        return found, self.args_found


    def inside(self, o, args):
        """ Checks if one of `args` inside an object `o` """
        for arg in args:
            if isinstance(o, str) and isinstance(arg, str) and re.search(arg, o, re.IGNORECASE):
                self.args_found.add(arg)
            elif arg == o:
                self.args_found.add(arg)


    def includes(self, structure, *args):
        """ Recursively search in a structure """
        if isinstance(structure, (str, int, bool, float)):
            new_args = self.inside(structure, args)
        elif isinstance(structure, (list, tuple, set)):
            for item in structure:
                self.includes(item, *args)
        elif isinstance(structure, dict):
            for key, value in structure.items():
                self.includes(key, *args)
                self.includes(value, *args)
        else:
            print(f"Undefind for structure {type(structure)}")