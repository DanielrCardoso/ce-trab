from mesa import Agent


class TreeCell(Agent):
    """
    A tree cell.

    Attributes:
        x, y: Grid coordinates
        condition: Can be "Fine", "On Fire", or "Burned Out"
        unique_id: (x,y) tuple.

    unique_id isn't strictly necessary here, but it's good
    practice to give one to each agent anyway.
    """

    def __init__(self, pos, model,reborn_tree):
        """
        Create a new tree.
        Args:
            pos: The tree's coordinates on the grid.
            model: standard model reference for agent.
        """
        super().__init__(pos, model)
        self.pos = pos
        self.condition = "Fine"
        self.reborn_tree = reborn_tree

    def step(self):
        """
        If the tree is on fire, spread it to fine trees nearby.
        """
        if self.condition == "Burned Out":
            for neighbor in self.model.grid.neighbor_iter(self.pos):
                if self.reborn_tree <= self.random.random():
                    self.condition = "Fine"


        if self.condition == "On Fire":
            for neighbor in self.model.grid.neighbor_iter(self.pos):
                if neighbor.condition == "Fine":
                    neighbor.condition = "On Fire"
            self.condition = "Burned Out"

