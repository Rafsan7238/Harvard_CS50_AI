import sys

from crossword import *
import copy

class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        w, h = draw.textsize(letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        for variable in self.domains:
            for value in self.domains[variable].copy():
                if len(value) != variable.length:
                    self.domains[variable].remove(value)

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        revision_made = False
        overlap = self.crossword.overlaps[x, y]

        if overlap is not None:
            for x_word in self.domains[x].copy():
                delete_x_word = True

                # if there is atleast 1 y_word that satisfies overlap, then x_word will stay
                for y_word in self.domains[y]:
                    if x_word[overlap[0]] == y_word[overlap[1]]:
                        delete_x_word = False
                        break

                if delete_x_word:        
                    self.domains[x].remove(x_word)
                    revision_made = True

        return revision_made

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        if arcs is None:
            arcs = []

            for variable in self.crossword.variables:
                for neighbour in self.crossword.neighbors(variable):
                    arcs.append((variable, neighbour))

        for pair in arcs:
            if self.revise(*pair):

                # if no word is left in the domain of a variable
                if not self.domains[pair[0]]:
                    return False

                # if a change is made, need to re-append the checked pairs
                for neighbour in self.crossword.neighbors(pair[0]):
                    arcs.append((neighbour, pair[0]))

        return True

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        for variable in self.crossword.variables:
            if variable not in assignment.keys():
                return False

        return True

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """

        # check if all values are unique
        if len(assignment) != len(set(assignment.values())):
            return False

        # check unary constraint
        for key, value in assignment.items():
            if key.length != len(value):
                return False

        #check binary constraints
        for key, value in assignment.items():
            for neighbour in self.crossword.neighbors(key):
                if neighbour in assignment.keys():
                    overlap = self.crossword.overlaps[key, neighbour]
                    if value[overlap[0]] != assignment[neighbour][overlap[1]]:
                        return False

        return True

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        number_of_choices_eliminated = {word: 0 for word in self.domains[var]}

        unassigned_neighbours = self.crossword.neighbors(var) - assignment.keys()

        for var_word in self.domains[var]:
            for neighbour in unassigned_neighbours:
                overlap = self.crossword.overlaps[var, neighbour]

                for neighbour_word in self.domains[neighbour]:
                    if var_word[overlap[0]] != neighbour_word[overlap[1]]:
                        number_of_choices_eliminated[var_word] += 1

        # sort the list in ascending order of values they rule out for neighbouring variables
        sorted_list = sorted(number_of_choices_eliminated.items(), key=lambda x:x[1])
        list_to_return = [x[0] for x in sorted_list]
        return list_to_return

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        unassigned_variables = self.crossword.variables - assignment.keys()

        # number of remaining values in each variable's domain
        num_remaining_values = {variable: len(self.domains[variable]) for variable in unassigned_variables}
        sorted_num_remaining_values = sorted(num_remaining_values.items(), key=lambda x:x[1])

        # if no tie, return variable with minimum number of remaining values in domain
        if len(sorted_num_remaining_values) == 1 or sorted_num_remaining_values[0][1] != sorted_num_remaining_values[1][1]:
            return sorted_num_remaining_values[0][0]

        #if tie, return variable woth highest degree
        else:
            num_degrees = {variable: len(self.crossword.neighbors(variable)) for variable in unassigned_variables}
            sorted_num_degrees = sorted(num_degrees.items(), key=lambda x:x[1], reverse=True)
            return sorted_num_degrees[0][0]


    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        if self.assignment_complete(assignment):
            return assignment

        variable = self.select_unassigned_variable(assignment)
        for value in self.order_domain_values(variable, assignment):
            assignment_copy = copy.deepcopy(assignment)
            assignment_copy[variable] = value

            if self.consistent(assignment_copy):
                assignment[variable] = value
                result = self.backtrack(assignment)

                if result is not None:
                    return result

            assignment.pop(variable, None)
        return None


def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
