import argparse

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--string', type=str)

    args = parser.parse_args()

    print(args.string)

if __name__ == "__main__":
    main()