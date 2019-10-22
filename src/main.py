import src.LoadData as data_loader


def main():
    # Load data from MySQL database
    data_loader.load_from_sql()


if __name__ == "__main__":
    main()