from pyDatalog import pyDatalog

pyDatalog.create_terms('X, Y, Z')
pyDatalog.create_terms('user, needs, product, solve_need, recommend')

# Defining user needs
+needs('Alice', 'Communication')
+needs('Bob', 'Knowledge')
+needs('Charlie', 'Physical Activity')
+needs('Diana', 'Fashion Statement')
+needs('Alex', 'Fashion Statement')
+needs('Alex', 'Food Preservation')  # Eve needs something for food preservation

# Defining products and how they solve specific needs
+solve_need('Smartphone', 'Communication')
+solve_need('Laptop', 'Communication')
+solve_need('Sci-Fi Novel', 'Knowledge')
+solve_need('Biography', 'Knowledge')
+solve_need('Tennis Racket', 'Physical Activity')
+solve_need('Running Shoes', 'Physical Activity')
+solve_need('Dress', 'Fashion Statement')
+solve_need('Handbag', 'Fashion Statement')
+solve_need('Eco-Friendly Fridge', 'Food Preservation')  # Fridge solves food preservation need
+solve_need('Compact Fridge', 'Food Preservation')

# Rule: Recommend a product to a user if the product can solve the user's need
recommend(X, Y)<= needs(X, Z) & solve_need(Y, Z)

# Query recommendations for each user
user_name = 'Alex'
# for user_name in ['Alex']:
#     print(f"Recommendations for {user_name}: {recommend(user_name, Y)& needs(X, Z) & solve_need(Y, Z)}")

results = needs(X, Z) & recommend(user_name, Y) &  solve_need(Y, Z)

for result in results:
    print(result[0], " -> ",result[1], " -> ", result[2])