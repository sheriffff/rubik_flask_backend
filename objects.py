from commutator.commutator import expand, search


class Commutator:
    def __init__(self, form: str) -> None:
        """
        Initialize a commutator using either the simplified or full form.
        Args:
            form (str): either
                - the simplified form   U: [M, U2]
                - the full form         U M U2 M' U
        """
        if self.is_full_form(form):
            self.movement_list = self._parse_movement_list(form)
            self.full_form = " ".join(self.movement_list)
            self.simplified_form = search(form)[0].replace(",", ", ")
        else:
            self.simplified_form = form.replace(",", ", ")
            self.full_form = " ".join(self._parse_movement_list(expand(form)))

    @staticmethod
    def _parse_movement_list(full_form: str) -> list[str]:
        """
        Parse a full form string into a list of movements
        Args:
            full_form (str): like "U ML' R"
        Returns:
            list[str]: like ["U", "M", "L'", "R"]
        """
        while " " in full_form:
            full_form = full_form.replace(" ", "")

        # Split into individual moves
        moves = []
        i = 0
        while i < len(full_form):
            move = full_form[i]
            i += 1
            # Check if next character is a modifier (2 or ')
            if i < len(full_form) and full_form[i] in "2'":
                move += full_form[i]
                i += 1
            moves.append(move)

        return moves

    @staticmethod
    def is_full_form(form: str) -> bool:
        """
        Check if the form is a full form.

        Args:
            form (str): The form to check.

        Returns:
            bool: True if the form is a full form, False otherwise.
        """
        return "[" not in form

    def __repr__(self) -> str:
        """
        String representations
        """
        return f"{self.simplified_form}\n{self.full_form}"


if __name__ == "__main__":
    comm = Commutator("U:[M,U2]")
    print("Simplified Form:", comm.simplified_form)
    print("Full Form:", comm.full_form)

    print("\n")
    comm2 = Commutator("UM  U2M'U")
    print("Full Form:", comm2.full_form)
    print("Simplified Form:", comm2.simplified_form)
