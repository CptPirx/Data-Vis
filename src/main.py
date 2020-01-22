# Main
# Main script that will run everything

import src.LoadData as dataLoader
import src.DataManipulation as dataManipulator
import src.visualise as visualise
import cProfile


def main():
    # Load data from MySQL database
    # pr = cProfile.Profile()
    # pr.enable()

    results, regions, final_data = dataLoader.load_from_sql()

    # final_data = dataManipulator.run_manipulation(results, regions, '1880-1-1', '2019-1-1')
    # final_geo_data = dataManipulator.merge_geodata(final_data)

    # pr.disable()
    # pr.print_stats(sort='cumtime')

    visualise.visualise_results(final_data)


if __name__ == "__main__":
    main()