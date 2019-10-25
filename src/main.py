# Main
# Main script that will run everything

import src.LoadData as dataLoader
import src.DataManipulation as dataManipulator
import src.visualise as visualise
import pandas as pd


def main():
    # Load data from MySQL database
    data = dataManipulator.run_manipulation(dataLoader.load_from_sql(), '1990-1-1', '2000-1-1')
    visualise.visualise_results(data)


if __name__ == "__main__":
    main()