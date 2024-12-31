import random
import mysql.connector  # type: ignore
import streamlit as st
import matplotlib.pyplot as plt
import ast

# Function to create a connection to the MySQL database
def connect_db():
    return mysql.connector.connect(
        host="localhost",  # MySQL server
        user="root",  # Your MySQL username
        password="password",  # Your MySQL password
        database="tsp_db"  # The name of the database
    )

# Function to insert data into the MySQL table
def insert_into_db(solution, route_length):
    conn = connect_db()
    cursor = conn.cursor()
    insert_query = "INSERT INTO tsp_results (solution, route_length) VALUES (%s, %s)"
    cursor.execute(insert_query, (str(solution), route_length))  # Store the solution as a string
    conn.commit()
    cursor.close()
    conn.close()

# Function to generate a random solution
def randomsolution(tsp):
    cities = list(range(len(tsp)))
    solution = []
    for i in range(len(tsp)):
        randomcity = cities[random.randint(0, len(cities) - 1)]
        solution.append(randomcity)
        cities.remove(randomcity)
    return solution

# Function to calculate route length
def routelength(tsp, solution):
    routelength = 0
    for i in range(len(solution)):
        routelength += tsp[solution[i-1]][solution[i]]
    return routelength

# Hill climbing algorithm
def hill_climbing(tsp, initial_solution, max_iteration=1000):
    current_solution = initial_solution
    current_length = routelength(tsp, current_solution)
    for _ in range(max_iteration):
        neighbours = getneighbours(current_solution)
        best_neighbour, best_length = getbestneighbour(tsp, neighbours)
        
        if best_length < current_length:
            current_solution = best_neighbour
            current_length = best_length
        else:
            break
    return current_solution, current_length

# Function to generate neighbors
def getneighbours(solution):
    neighbours = []
    for i in range(len(solution)):
        for j in range(i + 1, len(solution)):
            neighbour = solution.copy()
            neighbour[i] = solution[j]
            neighbour[j] = solution[i]
            neighbours.append(neighbour)
    return neighbours

# Function to get the best neighbor
def getbestneighbour(tsp, neighbours):
    bestroutelength = routelength(tsp, neighbours[0])
    bestneighbour = neighbours[0]
    for neighbour in neighbours:
        currentroutelength = routelength(tsp, neighbour)
        if currentroutelength < bestroutelength:
            bestroutelength = currentroutelength
            bestneighbour = neighbour
    return bestneighbour, bestroutelength

# Streamlit visualization function
def plot_solution(tsp, solution):
    x, y = [], []
    for city in solution:
        x.append(city % 10)  # Example coordinates
        y.append(city // 10)
    x.append(x[0])  # Return to the starting city
    y.append(y[0])
    
    plt.figure(figsize=(6, 6))
    plt.plot(x, y, marker="o", linestyle="--", color="blue")
    plt.title("TSP Route Visualization")
    plt.xlabel("X Coordinate")
    plt.ylabel("Y Coordinate")
    st.pyplot(plt)

# Streamlit function to set the background image
def add_background_image(image_url):
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("{image_url}");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

# Main function to run the Streamlit app
def main():
    # Set background image
    add_background_image("https://wallpapercave.com/wp/KGkY3or.jpg")

    # Streamlit title
    st.markdown("""<h1 style="color:green; font-family:Georgia, serif;">Travelling Salesman Problem (TSP) - Hill Climbing</h1>""", unsafe_allow_html=True)
    
    # Streamlit description
    st.markdown("""<p style="color:blue; font-family:Arial, sans-serif;">This application solves the <strong>Travelling Salesman Problem (TSP)</strong> using the Hill Climbing algorithm.</p>""", unsafe_allow_html=True)

    # Input section: TSP matrix
    st.header("Input the Distance Matrix")
    tsp = st.text_area("Enter the distance matrix as a nested list (e.g., [[0,400,300],[400,0,300],[300,400,0]])")

    if st.button("Generate and Solve"):
        try:
            # Process input matrix
            tsp = ast.literal_eval(tsp)
            
            # Generate initial random solution
            initial_solution = randomsolution(tsp)
            st.write(f"**Initial Random Solution:** {initial_solution}")
            st.write(f"**Initial Route Length:** {routelength(tsp, initial_solution)}")

            # Perform Hill Climbing
            solution, length = hill_climbing(tsp, initial_solution)
            st.write(f"**Best Solution After Hill Climbing:** {solution}")
            st.write(f"**Final Route Length:** {length}")

            # Plot the solution (Route Visualization)
            plot_solution(tsp, solution)

            # Insert the result into MySQL
            insert_into_db(solution, length)
            st.success("Results successfully saved to MySQL!")

        except Exception as e:
            st.error(f"Error: {e}")

if __name__ == "__main__":
    main()
