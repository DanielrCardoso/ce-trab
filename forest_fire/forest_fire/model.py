from mesa import Model
from mesa.datacollection import DataCollector
from mesa.space import Grid
from mesa.time import RandomActivation
from mesa.batchrunner import BatchRunner
import datetime
from .agent import TreeCell


class ForestFire(Model):
    """
    Simple Forest Fire model.
    """

    def __init__(self, width=100, height=100, density=0.65,init_fire=0.1,reborn_tree=20):
        """
        Create a new forest fire model.

        Args:
            width, height: The size of the grid to model
            density: What fraction of grid cells have a tree in them.
        """
        # Set up model objects
        self.schedule = RandomActivation(self)
        self.grid = Grid(width, height, torus=False)

        self.datacollector = DataCollector(
            {
                "Fine": lambda m: self.count_type(m, "Fine"),
                "On Fire": lambda m: self.count_type(m, "On Fire"),
                "Burned Out": lambda m: self.count_type(m, "Burned Out"),
            }
        )

        # Place a tree in each cell with Prob = density
        for (contents, x, y) in self.grid.coord_iter():
            if self.random.random() < density:
                # Create a tree
                new_tree = TreeCell((x, y), self,reborn_tree=reborn_tree)
                # Set all trees in the first column on fire.    
                if x ==self.grid.height/2 and y==self.grid.width/2:
                    new_tree.condition = "On Fire"
                    
                self.grid._place_agent((x, y), new_tree)
                self.schedule.add(new_tree)


        self.running = True
        self.datacollector.collect(self)

    def step(self):
        """
        Advance the model by one step.
        """
        self.schedule.step()
        # collect data
        self.datacollector.collect(self)

        # Halt if no more fire
        if self.count_type(self, "On Fire") == 0:
            self.running = False

    @staticmethod
    def count_type(model, tree_condition):
        """
        Helper method to count trees in a given condition in a given model.
        """
        count = 0
        for tree in model.schedule.agents:
            if tree.condition == tree_condition:
                count += 1
        return count
def fine(model):
    return lambda model: model.count_type(model, "Fine")

def fire(model):
    return lambda model: model.count_type(model, "On Fire")

def burned(model):
    return lambda model: model.count_type(model, "Burned Out")

def run_batch():
    fix_params = {
        "height": 100,
        "width": 100,
    }

    variable_params = {
        "density": [0.5, 0.75, 0.9], 
        "init_fire": [10, 20, 40],
        "reborn_tree": [20,50,80]
    }

    experiments_per_parameter_configuration = 100
    max_steps_per_simulation = 10
    run_batch = BatchRunner(
        ForestFire,
        variable_params,
        fix_params,
        iterations = experiments_per_parameter_configuration,
        max_steps = max_steps_per_simulation,
        model_reporters = {
            "Fine": fine(ForestFire),
            "Fire": fire(ForestFire),
            "Burned Out": burned(ForestFire),
        },
    )

    run_batch.run_all()

    run_model_data = run_batch.get_model_vars_dataframe()

    now = datetime.datetime.now().strftime("%Y-%m-%d")
    file_name_suffix =  ("iter"+str(10) + "steps"+str(100)+"distancia"+now)
    run_model_data.to_csv("model_data"+file_name_suffix+".csv")