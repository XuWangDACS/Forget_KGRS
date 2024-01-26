from kanren import Relation, facts, run, var, conde

# Create variables
x = var()
y = var()

# Define a relation
parent = Relation()

# Add facts to the relation
facts(parent, ("Homer", "Bart"),
              ("Homer", "Lisa"),
              ("Abe", "Homer"))

# Define a rule for grandparent
def grandparent(x, y):
    z = var()
    print(f"Checking if {x} is a grandparent of {y}:")
    # Describing the logical condition in a human-readable way
    print(f"Is there a {z} such that {x} is a parent of {z} and {z} is a parent of {y}?")
    return conde([parent(x, z), parent(z, y)])

# Query the relation using the rule
print("Querying grandparent relationships")
results = run(0, y, grandparent("Abe", y))  # Who are Abe's grandchildren?
print(f"Grandchildren of Abe: {results}")
